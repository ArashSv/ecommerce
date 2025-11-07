from django.db.models import Count, Q
from apps.products.models import OptionValue

def filter_variants_by_options(product, options_dict: dict[str, str]):
    """
        filter by selected options.
        example :
            options_dict = {'color': 'red', 'ram': '16GB'}
    """

    if not options_dict:
        return product.variants.none()

    filters = Q()
    for option_name, option_value in options_dict.items():
        filters |= Q(option__name__iexact=option_name, value__iexact=option_value)

    selected_value_ids = list(OptionValue.objects.filter(filters).values_list('id', flat=True))

    if not selected_value_ids:
        return product.variants.none()

    qs = (
        product.variants
        .filter(option_values__value__in=selected_value_ids)
        .annotate(
            matched=Count(
                'option_values',
                filter=Q(option_values__value__in=selected_value_ids),
                distinct=True
            )
        )
        .filter(matched=len(selected_value_ids))
        .distinct()
        .select_related('default_stockrecord')
        .prefetch_related('option_values__option', 'stockrecords__warehouse')
    )
    return qs
