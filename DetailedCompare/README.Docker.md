## Building and running

tldr:
start docker engine / daemon / whatever
cd into Human-Free-HR
docker build -t detailedcompare -f DetailedCompare/Dockerfile .

This package comes without a tokenizer model. 
The only setup required is to choose and download a tokenizer from HuggingFace and save it to /model
For most purposes, the [mpnet-base](https://huggingface.co/microsoft/mpnet-base/tree/main) model gives the best results. 
During initialization, main.py looks for a model saved to /model. 
For a saved state you can `cp PATH/TO/MY/MODEL/* DetailedCompare/model/ `. 

### To use mpnet-base from Microsoft:

Make sure you have git-lfs installed (https://git-lfs.com).

`git lfs install`

Then cd into the DetailedCompare directory and:

`git clone https://huggingface.co/microsoft/mpnet-base`

### Further customization:

The default number of tokens is set at 1500. 
For a faster running deployment, precision may be sacrificed by decreasing this number.

The "chunk_size" parameter is set to use the model's embedding dimension by default. This can be changed if desired, but I'm not sure why you'd want to (or why I added this feature to begin with).

When you're ready, start your application by running:
`docker compose up --build`.

Your application will be available at http://0.0.0.0:8000.