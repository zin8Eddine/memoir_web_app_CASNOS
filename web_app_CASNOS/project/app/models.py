
from datetime import timedelta
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models import Sum
from decimal import Decimal
from django.db import models

class AssurerMalade(models.Model):
    phone_regex = r'^\+?213[5-7][0-9]{8}$'
    matricule = models.BigIntegerField(primary_key=True)
    nom = models.CharField(max_length=30)
    prenom = models.CharField(max_length=50)
    dateniassance = models.DateField(verbose_name='Date de naissance')
    tauxPriseCharge = models.IntegerField(
        choices=((100, '100%'), (80, '80%')), verbose_name='Taux de Prise en charge')
    lieuAdress = models.CharField(
        max_length=50, default='', verbose_name='Lieu Adresse')
    telephone = models.CharField(max_length=20, validators=[
                                 RegexValidator(regex=phone_regex)], default='')
    statusAjour = models.BooleanField(
        verbose_name='Statut à jour', help_text='Précisez si le statut est à jour')
    dateDebutDroit = models.DateField(verbose_name='Date début de droit')
    dateFinDroit = models.DateField(
        verbose_name='Date fin de droit', editable=False)
    total_consommation = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    class Meta:
        verbose_name = "Assuré Malade"
        verbose_name_plural = "Assurés Malades"

    def calculate_total_consommation(self):
        total_consommation = self.dureeconsomations_set.aggregate(
            total=Sum('consomationsmedicament__consommation_par_qnt'))['total']
        if total_consommation is None:
            total_consommation = 0
        self.total_consommation = total_consommation.quantize(Decimal('0.00'))
        self.save(update_fields=['total_consommation'])
    def __str__(self):
        return f"{self.nom} {self.prenom}"


class Medicament(models.Model):
    FORME_CHOICES = [
        ('comprimé', 'Comprimé'),
        ('capsule', 'Capsule'),
        ('sirop', 'Sirop'),
        ('suspension', 'Suspension'),
        ('gelule', 'Gélule'),
        ('patch', 'Patch'),
        ('suppositoire', 'Suppositoire'),
        ('inhalateur', 'Inhalateur'),
    ]

    codeMedicament = models.CharField(
        max_length=11, primary_key=True, verbose_name='Code Médicament')
    nomMedicament = models.CharField(
        max_length=49, verbose_name='Nom Médicament')
    forme = models.CharField(
        max_length=21, choices=FORME_CHOICES, verbose_name='Forme')
    dosage = models.CharField(max_length=31, verbose_name='Dosage')
    conditionnement = models.CharField(
        max_length=26, verbose_name='Conditionnement')
    prixPublic = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='Prix Public')

    def __str__(self):
        return self.nomMedicament


class DureeConsomations(models.Model):
    assurerMalade = models.ForeignKey(AssurerMalade, on_delete=models.SET_NULL, null=True,verbose_name='Assuré Malade')
    medicaments = models.ManyToManyField(
        Medicament, through='ConsomationsMedicament')
    start_date = models.DateField(verbose_name='Date de debut')
    end_date = models.DateField(editable=False,verbose_name='Date de fin')

    # Add other prescription attributes here

    def save(self, *args, **kwargs):
        self.end_date = self.start_date + timedelta(days=90)

        super().save(*args, **kwargs)

    class Meta:
        unique_together = ['assurerMalade', 'start_date', 'end_date']
        verbose_name = "Durée de Consommation"
        verbose_name_plural = "Durée de Consommation"

    def __str__(self):
        return f"DureeConsommation for {self.assurerMalade}"


class ConsomationsMedicament(models.Model):
    dureeConsomations = models.ForeignKey(
        DureeConsomations, on_delete=models.SET_NULL, null=True)
    medicament = models.ForeignKey(Medicament, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    consommation_par_qnt = models.DecimalField(
        max_digits=10, decimal_places=2, editable=False)


    def calculate_consommation_par_qnt(self):
        if self.dureeConsomations.assurerMalade.tauxPriseCharge == 80:
            result = float(self.medicament.prixPublic * self.quantity) * 0.8
        elif self.dureeConsomations.assurerMalade.tauxPriseCharge == 100:
            result = float(self.medicament.prixPublic * self.quantity)
        else:
            result = 0

        rounded_result = round(result, 2)
        return rounded_result

    def save(self, *args, **kwargs):
        self.consommation_par_qnt = self.calculate_consommation_par_qnt()
        super().save(*args, **kwargs)

        # Update the total consommation for the related AssurerMalade
        self.dureeConsomations.assurerMalade.calculate_total_consommation()

    def __str__(self):
        return f"ConsomationsMedicament for {self.dureeConsomations}"


