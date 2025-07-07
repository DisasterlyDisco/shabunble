# shabunble
Shareable unenterable docker images

## What is this?
This repo is the artifact of the work put into creating shareable uninspectable running code. This would at first glance seem quite easy to do, a notion I attribute to the opaqueness of the fundamental machine to us as programmers and computer users; the brute force burden of computation and the mindnumbing minutiae of electronic plumbing is abstracted away letting us interact with it on human terms. But, when we don't delude ourselves into thinking that our own ignorance is meritted by an inherent ineffability native to the world, we know that computing is just math. And math doesn't lie.

If the computer can calculate it, it is part of the computers whole computation. Code cannot be at once parseable and hidden. Any boundary we set on the computations in the computer is itself part of the computations. These statements represent my current understanding of this topic, and from this a simpler statement: I believe that it is impossible to at once run code on a computer while making that code uninspectable.

But I also believe that we don't truly have to make the code uninspectable, just sufficiently hard to inspect. Novel solutions like fully homomorphic encryption or specialised confidential computing hardware might make deter even the highly motivated. But in most cases we might be able to get away with utilizing the notion of opagueness mentioned earlier. If we just make it slightly harder to inspect the code at the expected level of asbtraction, then I expect that we'll stymie a good portion of unwanted inspections.

Thus, my current proposal while I look for something stronger.

## The Practical Proposal
Docker images are contain all the files needed to run a program along with meatadata describing how the image should be instantiated. When instantiating the image, a user can choose to overwrite the defaults set by this metadata, letting them run other code present in the image. This is useful if a user wants to inspect the image as they can instantiate it with a shell and do all the tasks that one normally would be able to when shelled into a computer.

But, if there is no shell binary present in the image, then it can't be instantiated with a shell. The same goes for other unwanted programs and operations. Thus if we build the image with only the barest of neccesities to run our code, then users can't run anything unwanted without modifying the image first in some way.

(Modifying the image is not hard, but we are banking on most users simply not knowing that that is a possibility.)

So here is what we do. We split the build of the image into two parts. In the first part we use to build the code, and we base all of this off of an image with all the tools we need to do this (a shell, curl, package managers, whatever is needed). Then we copy only the needed build code into the second part, which is based off of an image with only the bare necessities to run our code. Nothing else.

In the subdirectory `/unenterable_container` I have included the Dockerfile for an minimal example of this for a simple python app. In this toy example the first part of the build doesn't actually do anythin other than copying the python code from the surrounding environment (it is simple python, so nothing needs to be compiled). But the second part is the interesting one anyway. In it, I start with one of googles "distroless" images, and copy the python code over to it before setting the python code as the entrypoint for the image. Googles "distroless" images (available at https://github.com/GoogleContainerTools/distroless) have several flavors meant to run only one flavor of interpreted language (and others that only run compiled binaries) with no other ancillirary programs. This makes it hard to run anything but the intended entry point (in the toy example all entrypoints must be python code, and our app is the only python code present), a great boon, but also a great limitation. The final image is much more limited, is tailored for a specific use case and is ill suited for hybrid code bases with multiple interpreted languages.

Generally, the proposal hinges on having seperate build and deploy stages in the dockerfile and ensuring that the deploy stage is based on an image with only the bare necessities, which can either be a "distroless" image from google or other providers, or an image build completely from scratch.

## Current state (in the pursuit of perfection, not the practical)
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
Looking into confidential computing.


#### A log, I guess
Setting users in the Dockerfile does nothing to hinder importers of the image; it restricts the permissions of the processes running **inside** the container, but someone outside the container still have the permissions of the user they are logged in as. If that user has sufficient permissions from the host computer to `docker run <IMAGE>`, then it doesn't matter what the standard entrypoint or user has been defined as in the Dockerfile; these can be overwritten as part of the `docker run` command: `docker run --entrypoint=sh user=root -it <IMAGE>`. (`enterable_container` contains a simple Dockerfile for an image with a user and defined entrypoint for testing this.)

I followed this unconference talk by Eric Chiang: https://ericchiang.github.io/post/containers-from-scratch/

Further reading: https://github.com/coollog/build-containers-the-hard-way

A container image is simple to inspect and edit - it is just nested directories with metadata. There is no encryption, there is no obfuscation (other than knowing the docker or OCI image standard).