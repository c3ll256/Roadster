p = part('pendant')
# The source union contains the body, rim and both lettering rows.
# Read shared geometry so the merged copy follows changes to the original.
merged_scale = param('merged_scale', 1.0)
assert merged_scale > 0
merged_union = p.combined.scale(merged_scale).clean()
assert merged_union.is_valid and len(merged_union.solids()) == 1
merged = merged_union.solids()[0]
merged.color = srgb('#bfc1c4')
assert abs(merged.volume-p.combined.volume*merged_scale**3)<1e-4
print('Merged solids:',len(merged.solids()),'valid:',merged.is_valid)
print('Merged envelope mm:',merged.bounding_box().size,'scale:',merged_scale)
publish('merged',merged,'合并版挂坠',material='petg')