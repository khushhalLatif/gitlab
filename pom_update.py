from lxml import etree

def insert_elements_from_string(pom_path: str, xml_string: str):
    """
    Parses a multiline XML string and appends its root children to pom.xml
    """
    # Parse the existing pom.xml
    tree = etree.parse(pom_path)
    root = tree.getroot()

    # Wrap your multiline string in a root tag so it's valid XML
    wrapped = f"<root>{xml_string}</root>"
    new_elements = etree.fromstring(wrapped)

    # Append each element to the pom root
    for element in new_elements:
        root.append(element)

    # Write back, preserving XML declaration
    tree.write(pom_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")
    print("Elements inserted successfully.")


# --- Your multiline XML string ---
new_xml = """
<dependencies>
    <dependency>
        <groupId>org.springframework</groupId>
        <artifactId>spring-core</artifactId>
        <version>5.3.0</version>
    </dependency>
</dependencies>

<plugins>
    <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.8.1</version>
    </plugin>
</plugins>

<properties>
    <java.version>17</java.version>
</properties>
"""

insert_elements_from_string("pom.xml", new_xml)