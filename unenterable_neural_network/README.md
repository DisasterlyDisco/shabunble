This "unenterable" image example has three parts: an image generator, a database and the actual image.

When all is up and running, the generator will write images to the database which the classifier inside the image will then poll and classify.

Minimum requirements for this example is to have python3 with venv and docker on the system.

### Step by step
1. **Setup the database** 
Add three secrets files to the `unenterable_neural_network/influxdb2/.env` subfolder with the following names and contents:
    * `influxdb2-admin-password` containing the admin password for the database.
    * `influxdb2-admin-token` containing the all access admin token for the database.
    * `influxdb2-admin-username` containing the admin username for the database.

    Then, spin up the database - from the `unenterable_neural_network/influxdb2` subfolder run `docker compose up influxdb2`. This might take a while.
    Log in to the database (should be at `https://localhost:8086`), using the previously set admin username and password.
    Navigate to the list of buckets and create a new one called `nn_deploy`.


2. **Create the database client config file**
In the `unenterable_neural_network` folder, create a new file called `config.ini`.
Fill it out with the following:
    ```
    [influx2]
    url=http://localhost:8086
    org=au
    token=<ADMIN TOKEN>
    timeout=6000
    verify_ssl=False
    ```

    replacing `<ADMIN TOKEN>` with the contents of `unenterable_neural_network/influxdb2/.env/influxdb2-admin-token`. (Alternatively, create a new token in the databse UI and use that instead, ensuring that it has read and write access to the `nn_deploy` bucket).

3. **Setup the Python virtual environment and install packages**
From `unenterable_neural_network` run `python3 -m venv .venv`. then source into the virtual environment `source .venv/bin/activate` and install the requirements `pip install -r requirements.txt`.

4. **Spin up the Docker Container**
From `unenterable_neural_network` run `docker compose up classifier`. This might take a while.

5. **Start the image generator**
From `unenterable_neural_network`, ensure that you've sourced the virtual environment and then run `python image_generator.py`. The first time this is run, the images that this "generates" is downloaded. This might take a while.


You should now have a process with the database, a process "generating" images for the database and a process containing the image reading from the databse and classifying those images.