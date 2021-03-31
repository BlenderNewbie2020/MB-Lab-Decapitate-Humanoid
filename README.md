# MB-Lab-Decapitate-Humanoid
Copy a humanoid head into a separate object retaining the shape keys

## Reasoning
Almost half the vertices and all but two of the shape keys are in the 'head'. Separating the head from the body reduces the shape key vertex count by _a lot_: eight to ten thousand vertices for eighty-plus shape keys.

This initial commit extracts the shape key data for the humanoid 'head' vertex group, rebases the shape keys for the reduced vertex count, copies the 'head' to a new object, and recreates the shape keys. The head expressions can be applied from Data > Shape Keys _and_ the MB-Lab tab Face Expressions button.

## TODO: 
Refactor vertex groups and remove redundancies.

The head is currently _duplicated_. It needs to be separated and the shape keys for the body recalculated. Unless you're Zaphod Beeblebrox.

# THIS IS A FIRST COMMIT: USE AT YOUR OWN RISK
