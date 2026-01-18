# Parametric Designs With Cadquery

You can find a few parametric design here, each model is a result of my own need. So they are just functional, not fancy. However you're welcome to make them fancier maybe more functional.

# How To ?

You need to have cadquery install on you system, CQ-editor is a nice to have tool to visualize and play with the models.

Check [CadQuery Documentation](https://cadquery.readthedocs.io/en/latest) for more information or any other installation problem. I highly recomend following cadquery documentation and running a few samples.

Install the cadquery along with other dependencies I have used in model scripts:
```bash
pip install -r requirements.txt
```

Well the rest is easy... just run the python script!

You can either change the box parameters in the script file or you can create JSON files to use to crete box. Better to use JSON files so you can save each config rather than chaging the script over and over. The parameters does not exists in JSON file are picked up script.

```bash
python3 pbox.py pbox_sample.json
```

# Models

## [pBox](PBOX_README.md)

Simple box you can generate to stome small things, not suggested in large sizes, or adjust the hidden parameters and make it work.

## [pIVAR](PIVAR_README.md)

Parametric box desing with lid, on which you can put some texts, for IKEA Ivar shelf. Hang(able) to Ivar shelf beams.
