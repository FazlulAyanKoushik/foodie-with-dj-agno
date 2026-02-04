from django.db import migrations

def seed_allergens(apps, schema_editor):
    Allergen = apps.get_model('restaurants', 'Allergen')

    mandatory_allergens = [
        ('Shrimp', 'えび'),
        ('Crab', 'かに'),
        ('Wheat', '小麦'),
        ('Buckwheat', 'そば'),
        ('Egg', '卵'),
        ('Milk', '乳'),
        ('Peanut', '落花生'),
    ]

    recommended_allergens = [
        ('Abalone', 'あわび'),
        ('Squid', 'いか'),
        ('Salmon Roe', 'いくら'),
        ('Mackerel', 'さば'),
        ('Salmon', 'さけ'),
        ('Orange', 'オレンジ'),
        ('Cashew Nut', 'カシューナッツ'),
        ('Kiwi Fruit', 'キウイフルーツ'),
        ('Peach', 'もも'),
        ('Apple', 'りんご'),
        ('Walnut', 'くるみ'),
        ('Banana', 'バナナ'),
        ('Yam', 'やまいも'),
        ('Soybean', '大豆'),
        ('Matsutake Mushroom', 'まつたけ'),
        ('Chicken', '鶏肉'),
        ('Pork', '豚肉'),
        ('Beef', '牛肉'),
        ('Gelatin', 'ゼラチン'),
        ('Sesame', 'ごま'),
        ('Almond', 'アーモンド'),
    ]

    for name, name_ja in mandatory_allergens:
        Allergen.objects.get_or_create(name=name, name_ja=name_ja, allergen_type='mandatory')

    for name, name_ja in recommended_allergens:
        Allergen.objects.get_or_create(name=name, name_ja=name_ja, allergen_type='recommended')

def remove_allergens(apps, schema_editor):
    Allergen = apps.get_model('restaurants', 'Allergen')
    Allergen.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0002_allergen_ingredients_allergens_menu_allergens'),
    ]

    operations = [
        migrations.RunPython(seed_allergens, remove_allergens),
    ]
