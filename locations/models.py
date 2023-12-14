from django.db import models


class Country(models.Model):
    code = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=63)
    lang = models.CharField(max_length=2)
    currency = models.CharField(max_length=31)
    dailing_code = models.CharField(max_length=7)
    phone_max_length = models.PositiveSmallIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Countries'
        ordering = ('created_at', )
        
    def __str__(self):
        return self.name


class State(models.Model):
    name = models.CharField(max_length=128)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    order = models.SmallIntegerField(default=0)

    class Meta:
        ordering = ('order',)
        constraints = [
            models.UniqueConstraint(
                fields=['country', 'name'], name='no_repeated_states_for_country')
        ]

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=128)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    order = models.SmallIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Cities'
        ordering = ('order',)
        constraints = [
            models.UniqueConstraint(
                fields=['state', 'name'], name='no_repeated_cities_for_state')
        ]

    def __str__(self):
        return self.name
