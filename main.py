from xsd2json_schemey.finder import find_type_elements

if __name__ == "__main__":
    # main()
    input_ = "/Users/tofarr/Downloads/efile1040x_2023v3.0/2023v3.0/IndividualIncomeTax/Ind1040/IRS1040/IRS1040.xsd"
    type_elements = find_type_elements(input_)
    # schema = xsd_to_json_schema(input_)
    print(type_elements)
