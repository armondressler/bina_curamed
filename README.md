# bina_curamed
School project (business intelligence &amp; analytics): Visualize parts of the curamed PIS (practice information system) datawarehouse

Goals:
  - Extends the curamed DWH insights with graphs.
  - The datasource is the curamed DWH.
  - The solution should present interactive graphs as part of a webpage, either standalone or as a component.
  - Provide insights (primarily economic and not medical perspective) into the workings of the practice. 
  
Praxisspiegel (Management Summary)

- https://www.trustmed.ch/Dienstleistungen/Management_Summary/Management_Summary.php
- https://www.hawadoc.ch/hawatrust/praxisspiegel-analyse.php
- http://www.zueridoc.ch/dienstleistungen/praxisspiegel-1qlik/
  
  
TODO:
- decent URL schema
  - GET /dashboards/business_overview
  - GET /dashboards/another_overview > 301 > /dashboards/another_overview?start_date=30daysago&end_date=today
  - 
- input validation for parameters (e.g. start_date/end_date iso 8601)
- default parameters? redirect to /x?start_date=30daysago&end_date=today
- cache (-> mark requests for past timeranges as cacheable?)
- any useful POST/PUT/DELETE?
