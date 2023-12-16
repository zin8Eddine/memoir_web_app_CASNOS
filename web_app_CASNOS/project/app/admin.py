from app.models import (AssurerMalade, ConsomationsMedicament,
                        DureeConsomations, Medicament)
from dateutil.relativedelta import relativedelta
from django.contrib import admin
from django import forms
from django.utils.html import mark_safe

class AssurerMaladeAdmin(admin.ModelAdmin):
    list_display = ['matricule', 'full_name', 'tauxPriseCharge', 'status_icon', 'dateDebutDroit', 'dateFinDroit', 'total_consommation']
    list_filter = ['statusAjour', 'tauxPriseCharge']
    search_fields = ['matricule', 'nom', 'prenom']
    readonly_fields = ['total_consommation']
    ordering = ['matricule']
    actions = ['make_status_ajour']
    
    def full_name(self, obj):
        return f"{obj.nom} {obj.prenom}"
    full_name.short_description = "Full Name"

    def status_icon(self, obj):
        if obj.statusAjour:
            return mark_safe('<img src="/static/admin/img/icon-yes.svg" alt="True">')
        else:
            return mark_safe('<img src="/static/admin/img/icon-no.svg" alt="False">')
    status_icon.short_description = 'Status Ajour'

    def make_status_ajour(self, request, queryset):
        queryset.update(statusAjour=True)
    make_status_ajour.short_description = "Mark selected records as 'Status Ajour'"

    def save_model(self, request, obj, form, change):
        if not change:  # Only calculate dateFinDroit when creating a new instance
            # Subtract one day from 12 months
            delta = relativedelta(months=12, days=-1)
            obj.dateFinDroit = obj.dateDebutDroit + delta
        else:
            # Calculate dateFinDroit if dateDebutDroit is modified
            previous_obj = self.model.objects.get(pk=obj.pk)
            if previous_obj.dateDebutDroit != obj.dateDebutDroit:
                delta = relativedelta(months=12, days=-1)
                obj.dateFinDroit = obj.dateDebutDroit + delta

        super().save_model(request, obj, form, change)


admin.site.register(AssurerMalade, AssurerMaladeAdmin)


class MedicamentAdmin(admin.ModelAdmin):
    list_display = ['codeMedicament', 'nomMedicament',
                    'forme', 'dosage', 'conditionnement', 'prixPublic']
    list_filter = ['forme']
    search_fields = ['codeMedicament', 'nomMedicament']
    list_per_page = 20

    # This is required for the autocomplete to work
    

admin.site.register(Medicament, MedicamentAdmin)


class ConsomationsMedicamentInline(admin.TabularInline):
    model = ConsomationsMedicament
    extra = 1
    raw_id_fields = ('medicament',)
    autocomplete_fields = ['medicament']



class DureeConsomationsForm(forms.ModelForm):
    class Meta:
        model = DureeConsomations
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        assurer_malade = cleaned_data.get('assurerMalade')
        
        # Check if the statusAjour of the AssurerMalade is False
        if assurer_malade and not assurer_malade.statusAjour:
            raise forms.ValidationError("You cannot add DureeConsomations for this AssurerMalade because the status is not up to date.")

    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        assurer_malade = self.cleaned_data.get('assurerMalade')
        
        if start_date:
            # Check if there are any existing DureeConsomations within the last 3 months
            three_months_ago = start_date - relativedelta(months=3)
            existing_duree_consomations = DureeConsomations.objects.filter(
                assurerMalade=assurer_malade,
                start_date__gte=three_months_ago,
                start_date__lte=start_date,
            ).exclude(pk=self.instance.pk if self.instance else None)  # Exclude current instance if editing
            
            if existing_duree_consomations.exists():
                raise forms.ValidationError("A DureeConsomations for this AssurerMalade already exists within the last 3 months.")
        
        return start_date

class DureeConsomationsAdmin(admin.ModelAdmin):
    form = DureeConsomationsForm
    list_display = ['assurerMalade', 'start_date', 'end_date']
    list_filter = ['assurerMalade__statusAjour', 'assurerMalade__tauxPriseCharge']
    search_fields = ['assurerMalade__matricule', 'assurerMalade__nom', 'assurerMalade__prenom']
    autocomplete_fields = ['assurerMalade']
    inlines = [ConsomationsMedicamentInline]
    list_per_page = 20
    readonly_fields = ['end_date']
admin.site.register(DureeConsomations, DureeConsomationsAdmin)