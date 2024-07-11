<a id="readme-top"></a>





<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="[https://github.com/othneildrew/Best-README-Template](https://github.com/agadin/Lake_viewer)">
    <img src="images/lake_view_logo.jpg" alt="Logo" width="300" height="300">
  </a>

  <p align="center">
    An Streamlit app to view your data!
    <br />
    <a href="https://lakeviewer.streamlit.app/"><strong>Access the Web App »</strong></a>
    <br />
    <br />
    <a href="(https://github.com/agadin/Lake_viewer">View the Github</a>
    ·
    <a href="https://github.com/agadin/Lake_viewer/releases">Get Current Release</a>
    ·
    <a href="https://lakelab.wustl.edu/">Lake Lab</a>
  </p>
</div>

# Lake Viewer

[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

An web based app to view, modify, and examine data! Additionally, ca

This repository contains:
1. Connect to GitHub or mannually upload `.txt` files as the data source
2. Modify `preferences.json` on GitHub
3. See most update data in easy to read metrics
4. Visualize data using interactable charts and tables

Lake ciewer is created to make data viewing easy for you! See [background](#background) section for more information!

## Table of Contents

- [Background](#background)
- [Install](#install)
- [Usage](#usage)
	- [Generator](#generator)
- [Badge](#badge)
- [Example Readmes](#example-readmes)
- [Related Efforts](#related-efforts)
- [Maintainers](#maintainers)
- [Contributing](#contributing)
- [License](#license)

## Background


## Install

This project can be hosted locally or visit [Lake Viewer Online](https://lakeviewer.streamlit.app/). For a python install, first create a folder on your computer and run the following commands.

**1. Install Python:**
Visit [Python.org](https://www.python.org/downloads/)

**2. Clone this github and unzip folder**
Open a terminal and enter:
```sh
git clone https://github.com/agadin/Lake_viewer
```

**3. Install dependences**
```
pip install streamlit
pip install -r requirements.txt

```

## Usage
> [!NOTE]
> This is instructions for a local install

To start the app navigate to the folder that was unzipped in terminal and run:

```sh
streamlit run app.py
```

Navigate to your web browser of choice and enter the address:
```
http://localhost:8501
```

The app should load into the settings page. The first step to using Lake View is to provide it with either the GitHub url that the rat wheel counter pushes to or to mannually upload .txt files. 

Using Github information to retrieve the data will also allow for the remote editing of the `preferences.json` file on the device through the app. To use the Github method, the github `user/repository_name` (the easiest way to find this would be to go to the repository url and copy inclusively the first the first the content between the first two slashes after github.com/) and a personal accesss access token that has read and write privaleges to the repository (see [GitHub personal access token](https://docs.github.com/en/enterprise-server@3.9/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) for more information). After succefully connecting the appy will display a success message and the Home page and the Wiki pages will update.

For the mannual upload, the .txt files have to be in the following format to be read correctly:
```
Date: Thursday 06/20/2024, Time: 00:00:00, Count: 1, Pin: D1
```
Note: for the mannual method all .txt files have to uploaded at once and the update `preferences.json` of the setting page will not work.



### Known Issues
* Logo does not render correctly on Wiki page :(
* The restore settings file upload does not work correctly and will not restore all settings. 



## Maintainers

[@agadin]([https://github.com/RichardLitt](https://github.com/agadin))

## Contributing

Feel free to dive in! [Open an issue](https://github.com/agadin/Lake_viewer/issues) or submit PRs.


### Contributors
[@agadin]([https://github.com/RichardLitt](https://github.com/agadin))


## License

[MIT](LICENSE) © Lake Lab


