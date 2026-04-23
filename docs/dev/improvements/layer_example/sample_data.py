"""Sample input layer.

Purpose:
- Hold a compact XML fixture for design review and prototype walkthroughs.

Boundary:
- Contains example data only.
- No domain logic, mapping logic, or document behavior.
"""

XML_INPUT = """<bk:catalog xmlns:bk="urn:books">
  <bk:book id="b1" lang="en">
    <bk:title>Original Title</bk:title>
    <bk:author>Alice</bk:author>
    <bk:author>Bob</bk:author>
    <bk:publisher>
      <bk:name>Northwind Press</bk:name>
    </bk:publisher>
  </bk:book>
  <bk:newspaper id="n1" lang="en">
    <bk:title>Daily Planet</bk:title>
    <bk:publisher>
      <bk:name>Planet Media</bk:name>
    </bk:publisher>
  </bk:newspaper>
</bk:catalog>
"""
