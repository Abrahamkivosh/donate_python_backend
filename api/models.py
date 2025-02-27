from django.db import models

class DonorProfile(models.Model):
    donor_id = models.IntegerField(unique=True)
    total_donations = models.IntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    avg_donation = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.IntegerField()
    last_donation_date = models.DateField()
    preferred_payment_method = models.CharField(max_length=50)
    recurring_donor = models.BooleanField(default=False)
    campaign = models.CharField(max_length=255)
    predicted_donation = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    next_donation_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Donor {self.donor_id}"
