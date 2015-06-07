# icimsDataImport
Imports Data from the iCims API into target database.

## Configure

Create a `settings.json` file in the same directory as `loadData.py` :

```json
{
    "icims_customer_number":"YOUR ICIMS CUSTOMER NUMBer",
    "icims_username":"ICIMS USERNAME",
    "icims_password":"ICIMS PASSWORD",
    "db_connection_string":"YOUR DB CONNECTION STRING"
}
```

## Run

1.	source venv/bin/activate
2.	sudo pip install requirements.txt
3.	python loadData.py


## To-do

1.	file structure