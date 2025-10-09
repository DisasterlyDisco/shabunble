from datetime import datetime, timezone
import time
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import sys
import torch
import torchvision
import torchvision.transforms as transforms

def tensor_to_point(tensor, point_name, label):
    point = Point(point_name)
    point.field("label", label)
    for x, sublist in enumerate(tensor.tolist()):
        for y, subsublist in enumerate(sublist):
            for z, pixel_value in enumerate(subsublist):
                point.field(f"{x},{y},{z}", pixel_value)
    return point

class Database():
    def __init__(self):
        self.client = InfluxDBClient.from_config_file("config.ini")
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.delete_api = self.client.delete_api()
        self.deploy_bucket = "nn_deploy"
        self.org = "au"

    def clear_bucket(self):
        start = datetime(1970, 1, 1, tzinfo=timezone.utc)
        stop = datetime.now(timezone.utc)
        self.delete_api.delete(
            start=start,
            stop=stop,
            predicate='',
            bucket=self.deploy_bucket,
            org=self.org
        )

    def save_image(self, image_tensor, label):
        with self.write_api as writer:
            writer.write(
                bucket=self.deploy_bucket,
                org=self.org,
                record=tensor_to_point(image_tensor, "image", label)
            )

def main():
    classes = ('plane', 'car', 'bird', 'cat',
               'deer', 'dog', 'frog', 'horse', 'ship', 'truck')
    
    print("〝(◉ϟ◉)〞// Connecting to InfluxDB...")
    db = Database()
    print("〝(◉ϟ◉)〞// Connected to InfluxDB")

    print("〝(◉ϟ◉)〞// Clearing bucket...")
    db.clear_bucket()
    print("〝(◉ϟ◉)〞// Bucket cleared!")
    
    transform = transforms.Compose(
    [transforms.ToTensor(),
     transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
    
    print("〝(◉ϟ◉)〞// Getting testset...")
    testset = torchvision.datasets.CIFAR10(root='./data', train=False,
                                       download=True, transform=transform)
    testloader = torch.utils.data.DataLoader(testset, batch_size=None,
                                         shuffle=False, num_workers=2)
    print("〝(◉ϟ◉)〞// Testset gotten!")

    print("〝(◉ϟ◉)〞// Uploading images to DB...")
    print("---")
    try:
        for image, label in iter(testloader):
            print(f"〝(◉ϟ◉)〞// Uploaded a {classes[label]}")
            db.save_image(image, label)
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n〝(-ϟ-)〞// Generator shutting down...", file=sys.stderr)
        db.clear_bucket()
        del db

if __name__ == "__main__":
    main()