from django.db import models
from django.utils import timezone
from datetime import date


def add_months(start_date, months):
    """Add months to a date, handling edge cases."""
    year = start_date.year + (start_date.month - 1 + months) // 12
    month = (start_date.month - 1 + months) % 12 + 1
    
    # Handle day overflow (e.g., Jan 31 + 1 month = Feb 28/29)
    if month == 2:
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            max_day = 29
        else:
            max_day = 28
    elif month in [4, 6, 9, 11]:
        max_day = 30
    else:
        max_day = 31
    
    day = min(start_date.day, max_day)
    return date(year, month, day)


class Member(models.Model):
    MAX_MEMBERS = 5000
    
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True, null=True)
    admission_date = models.DateField()
    plan_months = models.IntegerField(default=1)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2)
    next_due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.pk:  # New member
            # Check member limit
            if Member.objects.count() >= self.MAX_MEMBERS:
                raise ValueError(f"Member limit of {self.MAX_MEMBERS} has been reached.")
            # Set next_due_date if not already set
            if not self.next_due_date:
                self.next_due_date = add_months(self.admission_date, self.plan_months)
        super().save(*args, **kwargs)
    
    def get_status(self):
        """Get payment status based on next_due_date."""
        today = date.today()
        days_until_due = (self.next_due_date - today).days
        
        if days_until_due < 0:
            return {'code': 'overdue', 'label': 'Overdue'}
        elif days_until_due <= 3:
            return {'code': 'due-soon', 'label': 'Due Soon'}
        else:
            return {'code': 'ok', 'label': 'OK'}


class Payment(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_on = models.DateField()
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-paid_on']
    
    def __str__(self):
        return f"Payment of {self.amount} for {self.member.name} on {self.paid_on}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update member's next_due_date
        self.member.next_due_date = add_months(self.member.next_due_date, self.member.plan_months)
        self.member.save()

