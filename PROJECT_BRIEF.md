# Brief projet - Reconstruction propre du generateur de carrousels TikTok

## Objectif

Recreer le projet proprement de A a Z, en gardant les memes fonctionnalites que la version actuelle.

Aujourd'hui, le vrai produit est un generateur personnel de carrousels TikTok oriente plantes / Leafee :

1. generation de contenu via Gemini ;
2. generation d'images via Runware ou Replicate ;
3. composition des slides avec overlay texte ;
4. preview du carousel final ;
5. publication possible sur TikTok via upload-post.com ;
6. historique des generations ;
7. configuration des prompts depuis le dashboard.

Le but de la reconstruction n'est pas de changer le produit, ni d'en faire un SaaS public. Le but est de reprendre exactement les capacites existantes, mais dans une architecture plus claire, plus maintenable et plus simple a heberger.

## Produit cible

Une application web privee permettant de generer des carrousels TikTok prets a publier.

L'utilisateur doit pouvoir :

- entrer un mot-cle ou une idee ;
- choisir un type de contenu ;
- generer le texte du carousel ;
- generer les images correspondantes ;
- modifier manuellement les slides ;
- modifier les prompts d'image ;
- choisir le modele de generation d'image ;
- utiliser une reference selfie pour la premiere slide ;
- injecter automatiquement l'image Leafee sur la slide dediee ;
- appliquer un template visuel ;
- previsualiser une slide ou le carousel complet ;
- publier sur un ou plusieurs comptes TikTok ;
- retrouver ses anciennes generations dans un historique ;
- ajuster les prompts Gemini depuis une page de configuration.

Le projet doit rester personnel. Il n'y a pas besoin de comptes utilisateurs publics, de paiement, de permissions complexes ou de fonctionnalites marketing.

## Fonctionnalites a reprendre exactement

### Dashboard

Le dashboard actuel contient trois zones principales a conserver.

#### Accueil

La page d'accueil sert de point d'entree simple avec des liens vers :

- l'editeur de carrousel ;
- la configuration des prompts.

#### Editeur de carrousel

C'est le flux principal du produit.

Il doit permettre :

- saisie d'un keyword ;
- choix du type de contenu ;
- choix du nombre de slides ;
- ajout d'instructions custom optionnelles ;
- choix du modele image ;
- generation du contenu complet ;
- generation du contenu seul ;
- generation des images manquantes ;
- regeneration d'une seule image ;
- edition manuelle de chaque slide ;
- edition des prompts image ;
- choix du template par slide ;
- choix de la couleur du bandeau/titre ;
- upload manuel d'une image de fond ;
- selection d'une image selfie preset ;
- upload d'une reference selfie custom ;
- recuperation automatique de l'image Leafee ;
- preview d'une slide ;
- generation du carousel final ;
- preview du resultat final ;
- publication TikTok ;
- ouverture d'une generation depuis l'historique ;
- suppression d'une entree d'historique.

#### Configuration des prompts

La page de configuration des prompts doit permettre :

- afficher les 15 types de contenu disponibles ;
- previsualiser le prompt Gemini final pour un keyword d'exemple ;
- ajouter des instructions supplementaires par type de contenu ;
- remplacer completement le prompt d'un type via `full_prompt` ;
- utiliser les placeholders `{keyword}` et `{num_slides}` ;
- sauvegarder les overrides dans un fichier persistant.

## Workflow utilisateur actuel a conserver

Le workflow principal doit rester lineaire :

1. L'utilisateur ouvre l'editeur.
2. Il entre un keyword.
3. Il choisit un type de contenu.
4. Il choisit le nombre de slides.
5. Il ajoute eventuellement des instructions custom.
6. Il lance la generation du contenu via Gemini.
7. Le backend retourne un JSON structure.
8. L'utilisateur peut corriger les textes et prompts.
9. Il choisit un modele image.
10. Il choisit une reference selfie pour la premiere slide.
11. Il genere les images manquantes.
12. Il peut regenerer une image specifique.
13. La slide Leafee utilise l'image fixe `assets/leafee.jpg`.
14. Il genere le carousel final avec overlay.
15. Il verifie la preview.
16. Il publie sur TikTok ou garde les images finales.
17. La generation est disponible dans l'historique.

Le comportement important a conserver : la generation d'images ne doit pas remplacer les images deja presentes si elles existent. Elle doit cibler les images manquantes, sauf regeneration explicite d'une slide.

## Types de contenu

Le projet doit conserver les 15 types de contenu existants.

| ID | Nom | Nombre de slides typique | Role |
|---|---|---:|---|
| `care-guide` | Guide d'entretien | 6 | Conseils d'entretien plante |
| `hooks` | Hooks viraux plantes | 6 | Problemes/plantes qui meurent |
| `astrology` | Plantes par signe | 7 | Association signe astrologique/plante |
| `demographic` | Gen Z / Boomer / Millennial | 6 | Angle generationnel |
| `decor` | Plante selon deco | 7 | Plantes selon style interieur |
| `room` | Plante par piece | 6 | Plantes selon piece de la maison |
| `gift` | Idees cadeau | 6 | Cadeaux plantes |
| `valentine` | Saint-Valentin | 6 | Angle couple/amour |
| `birthday` | Anniversaire him/her | 6 | Idees anniversaire |
| `accessories` | Accessoires | 6 | Vases, pots, arrosoirs |
| `humidity` | Plantes humidite | 6 | Plantes pour pieces humides |
| `couple-zodiac` | Combo couple = plante | 6 | Signe couple vers plante |
| `top-x` | Top 5 par categorie | 7 | Classement thematique |
| `top-signs` | Top 5 signes | 7 | Classement astrologique |
| `before-after` | Avant / Apres | 6 | Transformation plante/deco |

Chaque type de contenu doit avoir :

- un identifiant stable ;
- un nom affiche dans l'interface ;
- un placeholder de keyword ;
- une description ;
- une fonction ou configuration de prompt ;
- un schema JSON attendu ;
- la possibilite d'etre override depuis l'interface.

## Format du contenu genere

Gemini doit retourner un objet compatible avec la structure actuelle :

```ts
type CarouselContent = {
  intro_title: string;
  intro_body: string;
  tips: {
    tag: string;
    body: string;
  }[];
  caption: string;
  tiktok_description: string;
  image_prompts?: string[];
  history_id?: string | null;
};
```

Contraintes a conserver :

- contenu en anglais, ton casual et viral ;
- format pense pour TikTok ;
- textes courts et lisibles ;
- pas de paragraphes longs ;
- integration soft de Leafee ;
- `caption` courte ;
- `tiktok_description` utilisable pour la publication ;
- `image_prompts` alignes avec les slides.

## Structure des slides

Le carousel contient :

- une slide intro ;
- plusieurs slides tip ;
- une slide speciale Leafee ;
- une description TikTok ;
- des prompts image.

Structure de slide pour le rendu :

```ts
type SlideContent = {
  type: "intro" | "tip";
  title?: string;
  body?: string;
  tag?: string;
  template_id?: string;
  title_bg_color?: string;
};
```

Comportements a conserver :

- la premiere slide est toujours traitee comme une intro ;
- la premiere slide peut utiliser une image de reference selfie ;
- la slide Leafee utilise une image fixe, pas une generation IA ;
- les autres slides utilisent les prompts image ;
- chaque slide peut avoir sa propre couleur de bandeau ;
- le template par defaut est `leafee-v2`.

## Generation de texte

La generation de texte doit rester basee sur Gemini.

Fonctionnalites a conserver :

- appel a Gemini avec un prompt construit par type de contenu ;
- support du keyword ;
- support du nombre de slides ;
- support d'instructions custom ;
- support du cache local de derniere reponse ;
- parsing JSON robuste ;
- sauvegarde de la generation dans l'historique ;
- retour d'un `history_id`.

Modele actuel a reprendre ou remplacer de facon equivalente :

- `gemini-3-flash-preview` ou modele Gemini equivalent ;
- variable `GEMINI_API_KEY`.

La reconstruction doit isoler cette logique dans un service clair, par exemple `TextGenerationService`, plutot que la disperser dans les routes.

## Generation d'images

Le projet doit conserver les trois options de generation d'image.

| ID UI | Service | Modele |
|---|---|---|
| `runware` | Runware | Flux 2 Klein |
| `replicate-gpt-image-2` | Replicate | OpenAI GPT Image 2 |
| `replicate-grok-imagine-image` | Replicate | xAI Grok Imagine |

Fonctionnalites a conserver :

- generation batch a partir des `image_prompts` ;
- generation d'une seule image ;
- choix du modele depuis le dashboard ;
- retries en cas d'echec ;
- fallback automatique vers Grok si le modele principal echoue et si Replicate est configure ;
- concurrence limitee pour eviter de saturer les APIs ;
- retour des images en base64 ;
- conservation de la `source_url` quand disponible ;
- sauvegarde des URLs dans l'historique ;
- support des prompts vides avec erreur par image ;
- support de `slide_indices` pour ecrire au bon index dans l'historique.

### Reference selfie

La premiere image doit pouvoir utiliser une reference selfie.

Sources a conserver :

- presets `fille1` a `fille9` ;
- upload local depuis l'interface ;
- URL distante ;
- base64 ;
- fallback automatique vers `assets/fille1.png`.

Comportement :

- la reference selfie ne s'applique qu'a l'image d'index `0` ;
- les autres slides n'utilisent pas cette reference ;
- si le preset est un ID interne comme `fille1`, le backend charge le fichier local et l'envoie en base64 au provider.

### Slide Leafee

La slide Leafee doit utiliser l'image fixe :

```text
assets/leafee.jpg
```

Cette image doit etre injectee automatiquement dans le flux. Elle ne doit pas etre regeneree par IA.

## Rendu du carousel final

Le rendu final doit conserver le fonctionnement actuel :

- format vertical TikTok ;
- sortie `1080x1920` ;
- JPEG qualite elevee ;
- overlay texte sur image ;
- template HTML ;
- screenshot via Playwright/Chromium ;
- fallback possible via PIL si Playwright n'est pas disponible.

Template actif a conserver :

```text
backend/templates/intro/leafee-v2.html
backend/templates/tip/leafee-v2.html
backend/templates/templates.json
```

Le rendu doit accepter :

- image de fond ;
- type de slide ;
- titre intro ;
- body intro ;
- tag tip ;
- body tip ;
- couleur de bandeau ;
- foreground PNG optionnel pour l'intro ;
- `template_id`.

Le endpoint ou service de rendu doit pouvoir :

- generer toutes les slides finales ;
- previsualiser une seule slide ;
- retourner les resultats en base64 ;
- limiter la concurrence des rendus.

## Couleurs et templates

Le systeme doit garder la logique de templates actuelle.

Fonctionnalites a conserver :

- chargement des templates disponibles ;
- templates intro et tip ;
- `template_id` par slide ;
- couleur de bandeau par slide ;
- palette globale Leafee dans l'interface ;
- application de la couleur aux templates compatibles ;
- fallback vers `leafee-v2` si le template demande n'existe pas.

Le projet n'a pas besoin d'un editeur graphique complet. Les templates peuvent rester simples et controles par HTML/CSS.

## Publication TikTok

La publication doit rester basee sur upload-post.com.

Fonctionnalites a conserver :

- publication d'un carousel photo ;
- envoi des slides finalisees avec overlay ;
- titre ;
- description TikTok ;
- mode de publication ;
- selection d'un ou plusieurs comptes ;
- boucle de publication sur les comptes selectionnes.

Modes a conserver :

- `DIRECT_POST` ;
- `MEDIA_UPLOAD`.

Parametres actuels a conserver :

- `privacy_level=PUBLIC_TO_EVERYONE` ;
- `auto_add_music=true` ;
- preservation des retours ligne dans la description.

Comptes actuels a reprendre, idealement en configuration plutot qu'en dur :

- `leftonreadgirl` ;
- `leftonreadgirlUS` ;
- `watereddownbf`.

Variables :

- `UPLOAD_POST_API_KEY` ;
- `UPLOAD_POST_USER`.

## Historique

Le projet doit conserver un historique des generations.

Comportements a reprendre :

- chaque generation de contenu cree une entree ;
- chaque entree a un `id` UUID ;
- conservation de la date ;
- conservation du keyword ;
- conservation du type de contenu ;
- conservation du nombre de slides ;
- conservation du prompt custom ;
- conservation du contenu Gemini ;
- conservation des images generees ;
- ouverture d'une entree depuis le dashboard ;
- suppression d'une entree ;
- limite d'environ 100 entrees.

Structure actuelle :

```ts
type ContentHistoryEntry = {
  id: string;
  created_at: string;
  keyword: string;
  content_type: string;
  num_slides: number;
  custom_prompt?: string | null;
  content: CarouselContent;
  generated_images?: {
    slide_index: number;
    image_model: string;
    source_url: string;
    filename?: string | null;
    mime?: string | null;
    generated_at: string;
  }[];
};
```

Stockage actuel a reprendre au minimum :

```text
data/content_history.json
```

Pour la reconstruction, il est possible de garder le JSON au depart. Si une base de donnees est ajoutee, elle doit reproduire exactement ce comportement.

## Configuration des prompts

Le projet doit conserver le systeme d'overrides.

Fichier actuel :

```text
data/prompt_overrides.json
```

Structure :

```ts
type PromptOverride = {
  extra_instructions: string;
  full_prompt?: string | null;
};
```

Regles :

- `extra_instructions` s'ajoute au prompt par defaut ;
- `full_prompt` remplace le prompt par defaut ;
- `full_prompt` peut utiliser `{keyword}` et `{num_slides}` ;
- la page config doit afficher le prompt final previsualise ;
- les changements doivent etre persistants sans modifier le code.

## API a conserver

Le backend doit proposer les memes capacites API.

Routes principales :

| Methode | Route | Role |
|---|---|---|
| `GET` | `/health` | Verifier que l'API tourne |
| `GET` | `/api/content-types` | Lister les types de contenu |
| `GET` | `/api/prompt-preview` | Previsualiser un prompt |
| `POST` | `/api/generate-content` | Generer le contenu Gemini |
| `GET` | `/api/content-history` | Lister l'historique |
| `GET` | `/api/content-history/{id}` | Ouvrir une entree |
| `DELETE` | `/api/content-history/{id}` | Supprimer une entree |
| `GET` | `/api/content-history/{id}/image/{slide_index}` | Recuperer une image historique |
| `POST` | `/api/generate-images-from-prompts` | Generer les images en batch |
| `POST` | `/api/generate-single-image` | Regenerer une image |
| `POST` | `/api/generate-carousel` | Composer le carousel final |
| `POST` | `/api/preview-slide` | Previsualiser une slide |
| `POST` | `/api/publish` | Publier sur TikTok |
| `GET` | `/api/templates` | Lister les templates |
| `GET` | `/api/girls-images` | Lister les presets selfie |
| `GET` | `/api/fille-image/{image_id}` | Recuperer un preset selfie |
| `GET` | `/api/leafee-image` | Recuperer l'image Leafee |
| `GET` | `/api/prompt-config` | Lire les overrides prompts |
| `POST` | `/api/prompt-config` | Sauvegarder les overrides prompts |

Les noms exacts peuvent etre conserves pour eviter de casser le dashboard. Si la nouvelle architecture change les chemins internes, le contrat API visible par le frontend doit rester equivalent.

## Architecture cible propre

La reconstruction doit separer les responsabilites sans changer le comportement.

Structure proposee :

```text
backend/
  app/
    main.py
    config.py
    api/
      routes/
        health.py
        content.py
        images.py
        carousel.py
        publish.py
        prompts.py
        assets.py
    services/
      text_generation.py
      prompt_builder.py
      image_generation.py
      carousel_renderer.py
      history_store.py
      prompt_config_store.py
      publisher.py
      asset_store.py
    content_types/
      registry.py
      base.py
      care_guide.py
      hooks.py
      astrology.py
      ...
    schemas/
      content.py
      images.py
      carousel.py
      history.py
      prompts.py
    templates/
      intro/
      tip/

dashboard/
  app/
    page.tsx
    editor/
      page.tsx
    config/
      page.tsx
  components/
    SlideEditor.tsx
    CarouselPreview.tsx
    ImageUploader.tsx
    TemplateSelector.tsx
  lib/
    api.ts
    types.ts
```

Principes :

- les routes FastAPI ne doivent pas contenir toute la logique metier ;
- les appels aux providers image doivent etre centralises ;
- le rendu carousel doit etre isole ;
- l'historique doit etre gere par un store dedie ;
- les prompts doivent etre versionnes ou au moins centralises ;
- le frontend doit rester simple et proche du workflow actuel.

## Frontend a reconstruire

Technologies recommandees :

- Next.js ;
- TypeScript ;
- Tailwind ;
- composants UI simples ;
- client API type.

Composants existants a reprendre dans l'esprit :

- `SlideEditor` ;
- `CarouselPreview` ;
- `ImageUploader` ;
- `TemplateSelector` ;
- client `api.ts` type.

Le frontend doit rester un dashboard personnel. Il n'a pas besoin d'etre fancy. La priorite est :

- flux clair ;
- boutons explicites ;
- preview lisible ;
- edition facile ;
- gestion des erreurs visible ;
- pas de surcharge visuelle.

## Backend a reconstruire

Technologies recommandees :

- Python ;
- FastAPI ;
- Pydantic ;
- Playwright ;
- Pillow en fallback ;
- stockage JSON au depart ou base legere si necessaire.

La premiere reconstruction peut rester sans base de donnees si cela simplifie le deploiement. Le stockage JSON est acceptable pour un outil personnel, a condition d'etre proprement encapsule.

Si une base est ajoutee plus tard, elle doit etre une evolution technique, pas un changement produit.

## Stockage et fichiers

Dossiers/fichiers a conserver ou recreer :

```text
data/content_history.json
data/prompt_overrides.json
data/gemini_last_response.json
assets/fille1.png
assets/fille2.png
assets/fille3.png
assets/fille4.png
assets/fille5.png
assets/fille6.png
assets/fille7.png
assets/fille8.png
assets/fille9.png
assets/leafee.jpg
assets/fonts/TikTokSans-Regular.ttf
backend/templates/intro/leafee-v2.html
backend/templates/tip/leafee-v2.html
backend/templates/templates.json
```

Fichiers legacy supprimes :

- `image_paths.json` ;
- `final_paths.json` ;
- `generated_content.json` ;
- `time_epoch.json` ;
- dossiers `carousel_images/` et `carousel_final/`.

## Variables d'environnement

Variables a documenter et conserver :

| Variable | Role |
|---|---|
| `GEMINI_API_KEY` | Generation texte Gemini |
| `RUNWARE_API_KEY` | Generation images Runware |
| `REPLICATE_API_TOKEN` | Generation images Replicate et fallback Grok |
| `REPLICATE_API_KEY` | Alias possible pour Replicate |
| `OPENAI_API_KEY` | Optionnel pour GPT Image 2 via Replicate |
| `UPLOAD_POST_API_KEY` | Publication TikTok |
| `UPLOAD_POST_USER` | Compte upload-post par defaut |
| `NEXT_PUBLIC_API_URL` | URL du backend pour le dashboard |
| `FONT_SCALE` | Ajustement taille texte overlay |
| `TIKTOK_FONT_PATH` | Police TikTok custom |

Pour l'hebergement, ajouter seulement si necessaire :

- `ADMIN_PASSWORD` pour proteger l'outil ;
- `APP_SECRET` si auth simple ;
- variables de stockage objet si les fichiers doivent persister hors disque local.

## Hebergement

Le projet doit pouvoir etre heberge en ligne pour un usage personnel.

Options simples :

- frontend Next.js sur Vercel ;
- backend FastAPI sur Render, Railway ou Fly.io ;
- ou une seule app sur VPS/Railway si c'est plus simple ;
- stockage local persistant si l'hebergeur le permet ;
- stockage objet plus tard si besoin.

Comme l'outil est prive, une protection simple suffit :

- mot de passe unique ;
- basic auth ;
- protection par l'hebergeur ;
- ou route non publique si usage tres personnel.

Pas besoin de :

- creation de comptes publics ;
- onboarding ;
- paiement ;
- quotas ;
- administration multi-user.

## Ce qui doit changer dans la reconstruction

Le produit doit rester le meme, mais le code doit etre plus propre.

A ameliorer :

- separer routes, services, schemas et stockage ;
- retirer la logique metier des composants trop gros ;
- eviter les chemins absolus ;
- centraliser la configuration ;
- rendre les providers image interchangeables ;
- isoler le renderer Playwright ;
- mieux nommer les dossiers ;
- documenter les endpoints ;
- documenter le format des donnees ;
- garder le code aligne avec le flux TikTok actuel ;
- eviter les secrets dans le repo ;
- rendre le deploiement reproductible.

## Ce qui ne doit pas changer sans raison

A conserver dans le comportement :

- les 15 types de contenu ;
- le schema Gemini ;
- les overrides de prompts ;
- l'historique ;
- les presets `fille1` a `fille9` ;
- l'image Leafee ;
- le template `leafee-v2` ;
- les trois modeles image ;
- le fallback Grok ;
- la preview slide ;
- la generation carousel ;
- la publication upload-post.com ;
- les comptes TikTok existants ;
- le format TikTok vertical ;
- le style general Leafee.

## Roadmap de reconstruction

### Phase 1 - Socle propre

- recreer la structure backend propre ;
- recreer la structure dashboard ;
- brancher les variables d'environnement ;
- remettre `/health` ;
- remettre le client API frontend ;
- remettre les assets essentiels.

### Phase 2 - Types de contenu et Gemini

- migrer les 15 types de contenu ;
- migrer le builder de prompts ;
- migrer les overrides ;
- recreer la preview de prompt ;
- recreer la generation de contenu ;
- recreer l'historique JSON.

### Phase 3 - Images

- recreer le service image ;
- brancher Runware ;
- brancher Replicate GPT Image 2 ;
- brancher Replicate Grok ;
- remettre retries et fallback ;
- remettre reference selfie ;
- remettre generation batch et single image ;
- sauvegarder les URLs dans l'historique.

### Phase 4 - Editeur

- reconstruire la page `/editor` ;
- remettre edition des slides ;
- remettre edition prompts image ;
- remettre upload image ;
- remettre presets selfie ;
- remettre couleur Leafee ;
- remettre chargement historique.

### Phase 5 - Rendu carousel

- migrer les templates HTML ;
- recreer le renderer Playwright ;
- remettre fallback PIL si utile ;
- remettre preview slide ;
- remettre generation finale base64 ;
- verifier le format `1080x1920`.

### Phase 6 - Publication

- migrer le client upload-post.com ;
- remettre publication `DIRECT_POST` ;
- remettre publication `MEDIA_UPLOAD` ;
- remettre publication multi-comptes ;
- tester avec les slides finalisees.

### Phase 7 - Deploiement

- ajouter une protection simple ;
- documenter le lancement local ;
- documenter les variables ;
- choisir l'hebergement ;
- tester le flux complet en production.

## Definition du succes

La reconstruction est reussie si le nouveau projet permet de faire tout ce que l'ancien permet deja :

- generer un contenu de carousel depuis un keyword ;
- choisir parmi les 15 types de contenu ;
- modifier les prompts et textes ;
- generer les images avec le modele choisi ;
- utiliser les presets selfie ;
- inserer la slide Leafee ;
- composer les slides finales ;
- previsualiser le resultat ;
- publier sur TikTok ;
- retrouver les anciennes generations ;
- configurer les prompts sans toucher au code ;
- heberger l'application en ligne pour usage personnel.

La difference doit etre dans la proprete du code, pas dans une perte de fonctionnalites.

## Resume court

Recreer proprement l'application existante de generation de carrousels TikTok Leafee. Le nouveau projet doit garder le meme workflow et les memes fonctionnalites : generation texte Gemini, 15 types de contenu, prompts configurables, generation images Runware/Replicate/Grok, reference selfie, slide Leafee fixe, overlay `leafee-v2`, preview, historique JSON et publication TikTok via upload-post.com. L'objectif est de nettoyer l'architecture et de rendre le projet hebergeable, sans transformer l'outil en SaaS complexe ni supprimer les capacites actuelles.
# Brief projet - Générateur de carrousels TikTok

