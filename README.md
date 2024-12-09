# datagrid

Create a datagrid of mixed-media items, and log to comet.com.

## Installation

```
pip install datagrid
```

## Example

The following demo program will log 100 random images, scores, and categories:

```python
from comet_ml import start
from datagrid import DataGrid, Image

import random
from PIL import Image as PImage
import requests

experiment = start(project_name="datagrids")

categories = ["sunset", "landscape", "water", "tree", "city"]

dg = DataGrid(
    columns=["Image", "Score", "Category"],
    name="Demo"
)
url = "https://picsum.photos/200/300"
for i in range(100):
    im = PImage.open(requests.get(url, stream=True).raw)
    category = random.choice(categories)
    score = random.random()
    image = Image(im, metadata={"category": category, "score": score})
    dg.append([image, score, category])

dg.log(experiment)
experiment.end()
```

## Visualization

![image](https://github.com/user-attachments/assets/a2a168cd-8e82-4418-b793-58e76bc5ab63)

Log into <a href="https://comet.com">comet.com</a> to see results.
