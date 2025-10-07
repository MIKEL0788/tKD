# Instructions pour l'importation de joueurs dans SparingTaKwDO

## Format de fichier requis

Le logiciel SparingTaKwDO accepte les formats de fichier suivants :
- CSV (.csv)
- Excel (.xlsx, .xls)

## Champs obligatoires

Votre fichier DOIT contenir les colonnes suivantes (avec exactement ces noms) :

1. `id` - Identifiant unique pour chaque joueur
2. `name` - Nom complet du joueur
3. `club` - Club d'appartenance
4. `country` - Pays (code à 3 lettres recommandé, ex: FRA, USA)
5. `category` - Catégorie du joueur (ex: "Senior Men -68kg")

## Champs optionnels

Vous pouvez également inclure ces colonnes optionnelles :

1. `weight` - Poids du joueur
2. `age` - Âge du joueur
3. `gender` - Genre (M/F)
4. `belt` - Ceinture/Grade

## Exemple de structure

Voici comment votre fichier doit être structuré :

| id   | name        | club               | country | category          | weight | age | gender | belt  |
|------|-------------|--------------------|---------|--------------------|--------|-----|--------|-------|
| P001 | Jean Dupont | Club Paris         | FRA     | Senior Men -68kg  | 67.5   | 25  | M      | Black |
| P002 | Marie Durand| Club Lyon          | FRA     | Senior Women -57kg| 56.8   | 23  | F      | Black |

## Points importants à vérifier

1. **En-têtes de colonnes** : Assurez-vous que les noms des colonnes sont exactement comme indiqué ci-dessus (sensible à la casse).
2. **Aucune colonne vide** : Les champs obligatoires ne doivent pas être vides.
3. **Format du fichier** : Si vous utilisez Excel, assurez-vous que les données sont dans la première feuille du classeur.
4. **Encodage** : Pour les fichiers CSV, utilisez l'encodage UTF-8 si possible.

## Exemples de fichiers

Deux fichiers d'exemple ont été créés dans le répertoire du logiciel :
- `exemple_format_correct.csv`
- `exemple_format_correct.xlsx`

Vous pouvez utiliser ces fichiers comme modèles pour créer votre propre fichier d'importation.

## Résolution des problèmes courants

- **"Le fichier n'est pas lisible"** : Vérifiez le format du fichier et l'encodage.
- **"Le contenu n'est pas ce qui est attendu"** : Vérifiez que les noms des colonnes sont corrects et que tous les champs obligatoires sont présents.
- **"Fichier incorrect"** : Assurez-vous que le fichier n'est pas corrompu et qu'il peut être ouvert normalement dans Excel ou un éditeur de texte.