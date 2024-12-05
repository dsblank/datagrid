# datagrid

Create a datagrid of mixed-media items, and log to comet.com.

## Installation

```
pip install datagrid
```

## Example

```python
from comet_ml import start
from datagrid import DataGrid, Image
import random
from PIL import Image as PImage
import requests

experiment = start(project_name="datagrids")

dg = DataGrid(columns=["Image", "Score"])
url = "https://picsum.photos/200/300"
for i in range(100):
    im = PImage.open(requests.get(url, stream=True).raw)
    dg.append([Image(im), random.random()])

dg.log(experiment)
experiment.end()
```

## Visualization

Log into comet.com to see results.

![image](https://github.com/user-attachments/assets/8ef86f1e-2a34-4b36-82d7-fca2929ebc38)
