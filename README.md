# bina_curamed
School project (business intelligence &amp; analytics): Visualize parts of the curamed PIS (practice information system) datawarehouse.


Goals:
  - Extend the curamed DWH insights with interactive visualisations.
  - The primary datasource is the curamed DWH, allow for additional datasources such as REST APIs.
  - The solution should present interactive graphs as part of a webpage, either standalone or as a component.
  - Provide insights (primarily economic and not medical perspective) into the workings of the practice.
  - Keep it easily to extend further
  
Installation:

Setup a virtualenv and activate it before running the pip install command.

```
python3 -m pip install -r requirements.txt
```

Running:
```
python3 app/main.py
```
  


TODO:
- decent URL schema
  - GET /dashboards/business-overview
  - GET /dashboards/another-overview > 301 > /dashboards/another-overview?start_date=30daysago&end_date=today

- auth
- input validation for parameters (e.g. start_date/end_date iso 8601)
- default parameters? redirect to /x?start_date=30daysago&end_date=today
- cache headers (-> mark requests for past timeranges as cacheable, excluding objects such as invoices)
