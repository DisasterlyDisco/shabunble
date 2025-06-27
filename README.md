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

This means that we can modify the image before running it to include a shell, voiding the "security advantage" of building a shell-less image.

For example:
The image build from the Dockerfile in `/unenterable_container` is based on the python version of Google's "distroless" images. This means that it boots directly into python, potentially running the python script that is set as the entrypoint. In the Dockerfile this is set to be the small python app copied from `/unenterable_container/python_app`. This app repeatedly counts down from 10 and shows an ASCII image of an explosion, taking no input. Stopping it stops the while container. But we can change the entrypoint as part of the `docker run` command, pointing it to a more usefull python app. No other app is on the image by default, but we can also specify a directory to be mounted on the image as part of the `docker run` command. Say, for instance, a directory containing a shell written in python called `mount_injection`.
From the repository root:
```
cd unenterable_container
docker build -t unenterable_boomline .
docker run -it -v $PWD/../mount_injection:/injection unenterable_boomline /injection/python_shell.py
```
The example python shell is very barebones, and several standard linux commands (like ls) are not present in the distroless image. But python is obviously a possible command, so at least we can run original python app:
```
python app.py
```
And if we have any other tools we want to use, we can add them as part of the mounted injection directory.

## Next step
Seeing if I can inhibit the inherent "inspectability" of a docker image.


#### A log, I guess
Setting users in the Dockerfile does nothing to hinder importers of the image; it restricts the permissions of the processes running **inside** the container, but someone outside the container still have the permissions of the user they are logged in as. If that user has sufficient permissions from the host computer to `docker run <IMAGE>`, then it doesn't matter what the standard entrypoint or user has been defined as in the Dockerfile; these can be overwritten as part of the `docker run` command: `docker run --entrypoint=sh user=root -it <IMAGE>`. (`enterable_container` contains a simple Dockerfile for an image with a user and defined entrypoint for testing this.)

I followed this unconference talk by Eric Chiang: https://ericchiang.github.io/post/containers-from-scratch/

Further reading: https://github.com/coollog/build-containers-the-hard-way

A container image is simple to inspect and edit - it is just nested directories with metadata. There is no encryption, there is no obfuscation (other than knowing the docker or OCI image standard).