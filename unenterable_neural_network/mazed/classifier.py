from datetime import timedelta
import time
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import numpy as np
import sys
import torch
import torch.nn as nn
import torch.nn.functional as F

PATH = '/deepest/darkest/depth/cifar_net.pth'

def point_to_tensor(record):
    image_array = np.zeros((3, 32, 32), dtype=np.float32)
    
    for field_name, value in record.values.items():
        if ',' in field_name:
            x, y, z = map(int, field_name.split(','))
            image_array[x, y, z] = value
    
    return torch.tensor(image_array)

class Database():
    def __init__(self):
        self.client = InfluxDBClient.from_config_file("config.ini")
        self.query_api = self.client.query_api()
        self.deploy_bucket = "nn_deploy"
        self.org = "au"
    
    def get_unprocessed_images(self, last_timestamp=None):
        if last_timestamp:
            # Add 1 microsecond to avoid reprocessing the last image
            next_timestamp = last_timestamp + timedelta(microseconds=1)
            timestamp_str = next_timestamp.isoformat()
            query = f'''
            from(bucket:"{self.deploy_bucket}")
              |> range(start: {timestamp_str})
              |> filter(fn: (r) => r._measurement == "image")
              |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
            '''
        else:
            query = f'''
            from(bucket:"{self.deploy_bucket}")
              |> range(start: -1h)
              |> filter(fn: (r) => r._measurement == "image")
              |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
            '''

        tables = self.query_api.query(query)
        return tables
    
    def __del__(self):
        self.client.close()
        

class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = torch.flatten(x, 1) # flatten all dimensions except batch
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


def classify_image(net, image_tensor):
    net.eval()
    with torch.no_grad():
        # Add batch dimension
        image_batch = image_tensor.unsqueeze(0)
        outputs = net(image_batch)
        _, predicted = torch.max(outputs, 1)
        return predicted.item()

def main():
    classes = ('plane', 'car', 'bird', 'cat',
               'deer', 'dog', 'frog', 'horse', 'ship', 'truck')
    
    print("(◡‿◡✿) ~ Loading neural network...")
    net = Net()
    net.load_state_dict(torch.load(PATH, weights_only=True))
    print("(◕‿◕✿) ~ Neural network loaded successfully!")
    
    print("(◕‿◕✿) ~ Connecting to InfluxDB...")
    db = Database()
    print("(◕‿◕✿) ~ Connected to InfluxDB")
    
    last_timestamp = None
    print("(◕‿◕✿) ~ Monitoring for new images...")
    print("---")
    
    try:
        while True:
            tables = db.get_unprocessed_images(last_timestamp)
            
            for table in tables:
                for record in table.records:
                    image_tensor = point_to_tensor(record)
                    
                    predicted_class_idx = classify_image(net, image_tensor)
                    predicted_class = classes[predicted_class_idx]
                    actual_class = classes[record.values.get("label")]
                    
                    timestamp = record.get_time()
                    
                    print(f"(◕‿◕✿) ~ This {actual_class} is a {predicted_class}!")
                    sys.stdout.flush()
                    
                    last_timestamp = timestamp
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n(◡‿◡✿) ~ Classifier shutting down...", file=sys.stderr)
        del db

if __name__ == "__main__":
    main()