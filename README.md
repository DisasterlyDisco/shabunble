# shabunble
Shareable unenterable docker images

## THE GOAL
Creating a docker image that cannot be entered or inspected after creation. This image should be extendable, and thus the actual product of this project will probably a process for making these images.

## THE ROAD
Meandering through the container jungle, meeting the Docker beast and becoming a addopted by the image tribe.

## Current state
I've managed to create a simple python app in a container that writes some silly stuff to the terminal without having a built in shell.
The Dockerfile and related sources are located in `/unenterable_container` if you want to try out the image.
That being said a container image is NOT an obfuscated file format. It is essentially a file structure (often tarred and compressed) with some metadata. Entering it is trivial (just unpack it). Protocol demands that they be immutable, but nothing stops an importer of an image from inspecting and mutating it BEFORE instantiating it.

## Next step
Seeing if I can inhibit the inherent "inspectability" of a docker image, and learning about linux namespaces