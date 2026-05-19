# Live2D Layer Spec

Use this as the target PSD layer naming map.

```text
000_body/
  010_torso_jacket
  020_neck
  030_choker

010_head/
  010_head_base
  020_muzzle
  030_nose
  040_front_hair
  050_back_hair
  060_cheek_shadow
  070_fur_highlights

020_horns_ears/
  010_left_horn
  020_right_horn
  030_left_ear
  040_right_ear

030_eyes/
  010_left_eye_white
  011_left_iris
  012_left_pupil
  013_left_eye_highlight
  014_left_upper_eyelid
  015_left_lower_eyelid
  020_right_eye_white
  021_right_iris
  022_right_pupil
  023_right_eye_highlight
  024_right_upper_eyelid
  025_right_lower_eyelid
  030_left_eyebrow
  040_right_eyebrow

040_mouth/
  010_upper_lip
  020_lower_lip
  030_mouth_inner
  040_upper_teeth
  050_lower_teeth
  060_tongue
  070_mouth_shadow

050_clothes/
  010_jacket_body
  020_left_collar
  030_right_collar
  040_zipper
  050_gold_trim_left
  060_gold_trim_right

060_optional_hands/
  010_left_hand
  020_right_hand
  030_pointing_hand

070_fx_optional/
  010_blue_energy_ring
  020_gold_sparks
```

## Layer Rules

- Each movable part should be separate.
- Horns must not be merged into the head base.
- Eyes, eyelids, iris, pupil, and highlights must be separable.
- Mouth inner, lips, teeth, and tongue must be separable.
- Gold tech lines on the jacket should be separated when possible.
- No logos, text, watermark, or copyrighted marks.

