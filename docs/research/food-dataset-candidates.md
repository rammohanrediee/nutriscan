# Food-image dataset and model candidates

**Status:** Research recommendation; no dataset approved for import or training

**Checked:** 26 October 2026

## Product target

NutriScan's evaluation distribution should prioritize:

1. everyday Indian tiffins and home meals such as idli, dosa, chapati/roti, poha, upma, rice,
   dal, sabzi, sambar, chutney, and curd;
2. protein-focused foods such as chicken, fish, eggs, paneer, tofu, sprouts, chana, and rajma;
3. fruit, vegetables, and salads;
4. realistic mixed meals and thalis; and
5. sweets, biryani, and street food only as lower-priority coverage.

The evaluation target is multi-food recognition plus rough visible portions and responsible
abstention. A fixed-class, single-label classifier is not a complete NutriScan model even when it
scores highly on its own test set.

## Ranked shortlist

| Rank | Candidate | Best role | Product status |
| ---: | --- | --- | --- |
| 1 | NutriScan-owned 30-image benchmark | Final selection authority | Required; keep private and held out |
| 2 | IndianFood61 | Multi-dish Indian platter training/research | Pursue access and written product terms |
| 3 | Indian Thali Dataset plus Weight Estimation Dataset | Segmentation and portion research | Pursue access and written product terms |
| 4 | FoodLens research dataset | Fine-grained, multi-label Indian taxonomy | Contact authors; no public reuse grant found |
| 5 | SOHL multi-dish | Small, immediately inspectable mixed-meal supplement | Audit provenance before product use |
| 6 | Enhanced Indian Food Classification | Broader single-dish research slice | Audit provenance before product use |
| 7 | Nutrition5k | Portion/weight methodology | CC BY 4.0, but non-Indian |

## Summary recommendation

No reviewed external dataset covers NutriScan's entire target with both strong annotations and a
clear product-compatible license. Use a portfolio:

- **Owned benchmark:** keep a small NutriScan-owned set of representative phone photos as the
  selection authority. This is the only way to guarantee the desired user distribution and avoid
  training-data leakage.
- **Immediate research supplement:** manually audit the SOHL multi-dish dataset and the Enhanced
  Indian Food Classification dataset from Hugging Face. They have the closest openly declared
  terms, but their source-image provenance and label quality still need verification.
- **Best multi-dish candidates to pursue:** request access and product-use terms for IndianFood61,
  the Indian Thali Dataset/Weight Estimation Dataset, and FoodLens. Their annotations align much
  better with the product than ordinary single-label classifiers.
- **Methodology reference:** use Nutrition5k to study weight/portion evaluation design, not as an
  Indian-food benchmark.
- **Do not import for a commercial product:** Khana, RASOI, FruitVeg-81, and FoodInsSeg are
  explicitly non-commercial or inherit restrictive source-image terms.

Do not combine an external model's training images with NutriScan's final held-out benchmark. A
model evaluated on its own training corpus can look excellent without generalizing to user photos.

## Candidate datasets

### 1. SOHL Multi-Dish Indian Food Detection Dataset - best small Hugging Face supplement

- Hub: [SohlHealth/sohl-multidish-yolo-dataset](https://huggingface.co/datasets/SohlHealth/sohl-multidish-yolo-dataset)
- Declared size: 377 images, 16 coarse classes, 2-6 items per plate, YOLOv8 boxes.
- Declared license: MIT.
- Relevant labels include roti/naan, curry, rice, dry vegetables, dal/sambar, eggs, fish, fruits,
  salads, accompaniments, and South Indian breakfast (dosa/idli/upma).
- Strength: unusually close to NutriScan's desired multi-dish distribution and includes diet-food
  groups missing from the current 15-class benchmark.
- Weakness: very small, only one published split, coarse labels merge visually and nutritionally
  different foods, and the card does not document image provenance or independent annotation QA.

**Audit checkpoint (27 October 2026):**

- Dataset URL: [SohlHealth/sohl-multidish-yolo-dataset](https://huggingface.co/datasets/SohlHealth/sohl-multidish-yolo-dataset)
- Exact immutable Hugging Face commit/revision:
  `ef83f6636e5d9e0593aeaecae49ef05ef418693a`.
- Pinned revision: [repository tree at `ef83f6636e5d9e0593aeaecae49ef05ef418693a`](https://huggingface.co/datasets/SohlHealth/sohl-multidish-yolo-dataset/tree/ef83f6636e5d9e0593aeaecae49ef05ef418693a).
- Declared license: dataset-card file `README.md`, YAML front matter key `license`, exact value
  `mit`. The [pinned dataset card](https://huggingface.co/datasets/SohlHealth/sohl-multidish-yolo-dataset/blob/ef83f6636e5d9e0593aeaecae49ef05ef418693a/README.md)
  also renders a `License` section stating "MIT License - See LICENSE file for details," but the
  pinned repository root does not contain the referenced `LICENSE` file.
- Original image source or rights holder named by the dataset card: **No.** The citation names the
  `SOHL AI Team` as author and the contact section names the same team, but neither statement
  identifies where the images originated or who owns their rights.
- **Status: Blocked pending further audit.** No images were downloaded, and the dataset is not
  approved.
- Interpretation: insufficient evidence to approve this source; these gaps do not establish
  misconduct by the publisher. Image checksums, independent label QA, original-versus-augmented
  status, and duplicate/leakage checks remain unverified.

**Decision:** inspect every image and annotation, verify source-image rights with the publisher,
deduplicate against all training sources, and use only as a research supplement. It is too small
and coarsely labelled to be the sole benchmark or production training set.

### 2. Enhanced Indian Food Classification - broader Indian single-food coverage

- Hub: [SohlHealth/enhanced-indian-food-classification](https://huggingface.co/datasets/SohlHealth/enhanced-indian-food-classification)
- Declared size: 15,404 images, 43 classes, with train/validation/test splits.
- Declared license: CC BY 4.0.
- Labels include chapati, chicken curry, dal makhani, fish curry, idli, masala dosa, poha, rajma
  curry, white rice, multiple paneer dishes, and other common dishes.
- Strength: substantially better everyday/protein coverage than the current 15-class public set.
- Weakness: still a single-label classification corpus; no fruit/salad coverage, portion labels,
  multiple-food annotations, documented collection provenance, or published QA method.

**Decision:** possible source for a stratified single-dish research slice after manual provenance,
duplicate, and split audits. Do not treat its declared license alone as proof that every underlying
image is product-cleared.

### 3. IndianFoodNet-30 - useful everyday dish boxes, research-only images

- Dataset page: [IndianFoodNet-30 on Roboflow](https://universe.roboflow.com/indianfoodnet/indianfoodnet/dataset/1)
- Paper: [IndianFoodNet: Detecting Indian Food Items Using Deep Learning](https://iieta.org/download/file/fid/117771)
- Source corpus described by the paper: more than 5,500 source images over 30 classes, collected
  from Google and Bing and annotated with bounding boxes. The Roboflow version reports 13,036
  generated examples after augmentation and train/validation/test splits.
- Roboflow displays CC BY 4.0, but the publisher's own fair-use notice says the corpus contains
  copyrighted material without specific authorization and is supplied for non-commercial academic
  research. Product use requires permission from the underlying copyright owners.
- Relevant classes include dal, dosa, fish curry, idli, poha, rajma curry, palak paneer, rice,
  chutneys, vegetable curries, and mutton curry.
- Strength: localized foods and stronger routine-meal coverage than snack-heavy classification
  datasets.
- Weakness: mostly single-item web images; the Roboflow counts include augmented outputs; search
  engine collection creates a source-rights question; fruit, salad, eggs, and mixed home plates are
  weak or absent.

**Decision:** research reference only. The explicit fair-use notice controls the product decision;
do not import these images for NutriScan without clearing the underlying rights.

### 4. IndianFood10/20 and IndianFood61 - strongest published Indian platter direction

- IndianFood10/20 paper: [Object Detection in Indian Food Platters](https://arxiv.org/abs/2205.04841)
- IndianFood61 paper: [Dish detection in food platters](https://arxiv.org/abs/2305.07552)
- IndianFood10 contains 11,547 annotated images for ten classes: aloo paratha, biryani,
  chapati, chicken tikka, khichdi, omelette, palak paneer, plain rice, poha, and rasgulla.
- Only 842 IndianFood10 images (about 7%) are multi-dish; those average 2.33 dishes per image. The
  paper says the images were scraped from Instagram hashtags, so access does not settle image rights.
- IndianFood20 extends it to 17,817 images and twenty classes.
- IndianFood61 reports 68,005 platter images and 134,814 manual dish annotations across 61 classes,
  supporting both multi-label classification and object detection.
- Strength: IndianFood61 is the closest published match for real Indian platter logging and
  includes difficult proteins such as chicken, mutton, and kebab.
- Weakness: access may require Google Drive/IEEE DataPort, exact product-use terms must be checked
  at download time, and the publicly described benchmark does not replace NutriScan's independent
  held-out photos.

**Decision:** highest-priority author/contact and licensing investigation. If product use is
permitted, sample it for training or supplementary evaluation while reserving independent
NutriScan photos for final scoring.

### 5. Indian Thali Dataset and Weight Estimation Dataset - best portion research direction

- Paper: [What is there in an Indian Thali?](https://cdn.iiit.ac.in/cdn/cvit.iiit.ac.in/images/ConferencePapers/2025/ICVGIP_Food_Scanner.pdf)
- Indian Thali Dataset: 7,900 views of 796 plates, 50 dishes, with pixel-level masks.
- Weight Estimation Dataset: 1,394 views of 267 plates, 41 dishes, with gram-level food-item
  weights.
- Strength: authentic multi-item thalis, multiple viewpoints, dense masks, and direct portion
  evidence are unusually well aligned with NutriScan.
- Weakness: the paper's controlled multi-view capture rig is different from one ordinary phone
  photo; the accessible project material reviewed did not establish product-use license terms.

**Decision:** contact the authors for dataset access and explicit commercial/product terms. Use it
to inform portion evaluation only after the license and capture-domain difference are resolved.

### 6. FoodLens research dataset - excellent multi-label taxonomy, not publicly usable yet

- Publication: [Google Research FoodLens](https://research.google/pubs/foodlens-fine-grained-and-multi-label-classification-ofindian-food-images/)
- Reported size: 30,000 Indian restaurant images and more than 140 dishes.
- Annotation: multi-label, fine-grained dish annotations organized into a hierarchy.
- Strength: strong cultural breadth and multi-label task alignment.
- Weakness: the official publication page reviewed does not provide a public dataset download or
  reuse license; restaurant-menu images may not represent home tiffins and meal-prep plates.

**Decision:** contact the authors. Do not assume paper availability means data availability.

### 7. DataCluster Indian Food Image Dataset - possible licensed commercial route

- Source: [DataCluster Indian Food Image Dataset](https://github.com/datacluster-labs/Indian-Food-Image-Dataset)
- Described size: about 3,500 mobile-phone images contributed by more than 5,000 users, with
  classification/detection and possible multi-category annotations.
- Strength: diverse phone capture, lighting, and indoor scenes are closer to real NutriScan use
  than search-engine images.
- Weakness: the full dataset and exact label taxonomy are not openly downloadable; price, license,
  consent/rights chain, and permitted model/product uses require a sales agreement.

**Decision:** ask for a class list, sample, annotation QA report, contributor release language, and
commercial license quote. This is a more credible product path than assuming rights to scraped web
images if its contracts prove adequate.

### 8. Khana - broad classification research, not product-cleared

- Homepage: [Khana](https://khana.omkarprabhu.in/)
- Declared size: more than 131,000 web images across 80 dishes.
- Useful labels include chapati, idli, multiple dosas, poha, pongal, chana masala, fish curry,
  paneer dishes, rajma chawal, and thali.
- Strength: broad Indian taxonomy and far more routine-food coverage than the existing public set.
- Weakness: single-label classification, no fruit/salad taxonomy, class imbalance, and the creators
  state they do not own the image copyrights.
- Terms: non-commercial research or educational use only.

**Decision:** taxonomy and research reference only; do not import images into a commercial
NutriScan training or benchmark corpus.

### 9. RASOI - relevant thali annotations, non-commercial

- Official lab page: [Food Computing Lab datasets](https://fkg-india.github.io/library/datasets/)
- Contains standalone recipes plus composite thalis with bounding boxes and dish labels.
- License: CC BY-NC-SA 4.0; the lab explicitly describes it as non-commercial research use.

**Decision:** useful research comparison, but not a product dataset without a separate commercial
license from the creators.

### 10. Global supplements

#### Nutrition5k

- Source: [Google Research Nutrition5k](https://github.com/google-research-datasets/Nutrition5k)
- 5,006 cafeteria plates with side videos, RGB-D where available, ingredient lists,
  per-ingredient mass, dish mass, calories, and macronutrients.
- License: CC BY 4.0, including commercial use with attribution.
- Limitation: collected in a few California cafeterias and explicitly not cuisine-complete.

**Decision:** strong reference for portion/weight benchmark methodology. Do not use it as evidence
that a model recognizes Indian tiffins or thalis.

#### FoodSeg103

- Source: [FoodSeg103 on Hugging Face](https://huggingface.co/datasets/AliJkr/FoodSeg103)
- 7,118 images, 103 ingredient categories, and pixel-wise annotations; labels include chicken,
  fish, egg, tofu, rice, salad, fruits, and many vegetables.
- Strength: fills protein, produce, and ingredient-segmentation gaps.
- License warning: the Hub mirror declares Apache 2.0, but the images are curated from Recipe1M;
  mirrors of the benchmark describe Recipe1M image terms as non-commercial/research and do not
  grant image redistribution. Treat the most restrictive source-image terms as controlling until
  counsel or the rights holder confirms otherwise.

**Decision:** research-only until the image-license chain is resolved. It is not culturally
specific enough to replace the Indian benchmark.

#### FruitVeg-81

- Source: [Graz University FruitVeg-81](https://www.tugraz.at/institute/icg/research/team-bischof/learning-recognition-surveillance/downloads/fruitveg)
- 15,737 images with hierarchical fruit/vegetable labels.
- Terms: non-commercial research only, no redistribution, with some image rights held by stores.

**Decision:** do not use for a commercial product. Create or license a small product-cleared fruit
and salad benchmark instead.

## Candidate model cards

Specialized models are useful baselines, but none reviewed here replaces the hosted vision-language
model benchmark.

| Model | Useful capability | Blocking limitation |
| --- | --- | --- |
| [prithivMLmods/Indian-Western-Food-34](https://huggingface.co/prithivMLmods/Indian-Western-Food-34) | 34-class Indian/Western reference classifier | One fixed label, no portions/abstention/multi-food output; not served by a Hub Inference Provider |
| [therealcyberlord/vit-indian-food](https://huggingface.co/therealcyberlord/vit-indian-food) | Reproducible 15-class baseline on the current public corpus | Same narrow, snack-heavy label space and trained on the dataset it reports against |
| [dima806/indian_food_image_detection](https://huggingface.co/dima806/indian_food_image_detection) | 80-class Indian single-dish baseline | Card reports about 75% validation accuracy; no multi-food or portion contract; not Provider-hosted |
| [arunapb/yolo11l-food-segmentation](https://huggingface.co/arunapb/yolo11l-food-segmentation) | Ingredient-level segmentation for proteins, fruits, vegetables, rice, tofu, and salad | Global rather than Indian labels; inherits FoodSeg103/Recipe1M license concerns; not Provider-hosted |
| [Alas-V/ConvNeXt-Food-CLF-75](https://huggingface.co/Alas-V/ConvNeXt-Food-CLF-75) | Multi-label ingredients including chicken, fish, egg, tofu, sprouts, fruits, vegetables, rice, and salad | Global ingredient labels, self-reported macro F1 0.655/mAP 0.714, hallucination risk, and no Inference Provider deployment |
| [Google Mobile Food Segmenter](https://tfhub.dev/google/seefood/segmenter/mobile_food_segmenter_V1/1) | Mobile-oriented food-region segmentation reference linked from Nutrition5k | Segments food regions; it does not supply Indian dish identity, portions, or NutriScan JSON |
| IndianFood61 YOLOv8x from the published study | Indian platter object detection with the strongest task alignment | Model artifact, access terms, and production license require direct verification |

The current hosted Qwen vision-language candidates remain better aligned with NutriScan's required
open-vocabulary, multi-item, strict-JSON response. Specialized classifiers should be evaluated as
research baselines only, never granted nutrition authority.

## Recommended benchmark composition

External datasets should supply candidate images, not dictate product priorities. A 30-image
held-out NutriScan set should contain:

- 12 everyday Indian tiffin/home-meal images;
- 8 protein-focused meal images;
- 5 fruit, vegetable, or salad images;
- 2 indulgent/street-food images; and
- 3 unclear or non-food controls.

Coverage tags may overlap. Require at least ten mixed meals and include home, restaurant,
takeaway, low-light, occlusion, and visually confusing pairs such as paneer/tofu and chicken/soy.
Keep exact benchmark images and labels private so candidate providers cannot train to them.

## Required audit before any dataset enters NutriScan

1. Record the exact revision, checksum, source URL, named rights holder, and license text.
2. Verify that the uploader owns or is authorized to license the underlying images; a repository
   license badge is not enough for web-scraped images.
3. Inspect label frequencies and a stratified image sample; document mislabeled, duplicate,
   generated, and augmented examples.
4. Deduplicate by content hash and perceptual similarity across train, validation, test, and the
   NutriScan benchmark.
5. Separate original photographs from augmented derivatives before reporting sample counts.
6. Map labels to NutriScan's canonical recognition vocabulary without converting visible guesses
   into nutrition facts.
7. Keep the selection benchmark held out from all tuning and prompt iteration.
8. Re-evaluate rights and dataset availability immediately before downloading or publishing any
   derived artifact.

## Current decision

Do not replace the benchmark with a single internet dataset. First audit the two small Hugging Face
candidates, contact the IndianFood61, Indian Thali/WED, and FoodLens owners, and prepare the owned
30-image product benchmark. No runtime model, dependency, database, route, or app implementation is
authorized until the separate vision-model selection gate records a winner.
