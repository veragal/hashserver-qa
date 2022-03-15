# hashserver-qa

Automated testing for hash server

# Environment setup

* Docker
* Python3 modules:
  - `requests`
  - `pytest`
  
# Insructions

Run the tests with the following command: 

```
pytest ./api_endpoints.py 
```

It will:
1. create a docker image with the hashserver pulled from Amazon AWS
2. run every test case in a separate Docker container and shut it down at the end of the test


# Test plan

Check the file ./test_plan.txt for the test plan and one bug report.
