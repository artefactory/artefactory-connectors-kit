from lib.utils.text import get_generator_dict_from_str_csv


def test_multiple_encodings():
    test_string_to_encode = (
        "BR,Sanofi Aventis Brasil,3945535,Active,Allegra,3992233,0,,"
        "YR_Sanofi_Allegra_201910_Consideration_DV360_Precision_"
        "Native-Ads_Cross-Device_BR,11140383,Active,,"
        "YR_Sanofi_Allegra_201910_Consideration_DV360_Precision_OA"
        "_Native-Ads_DV-Affinity-Health_Desktop_BR,"
        '1130016,0,,"    ",0.00,4080863'
    )
    lines = [
        b"Country,Partner,Partner ID,Partner Status,Advertiser,Advertiser ID,Advertiser Status,Advertiser Integration Code,Insertion Order,Insertion Order ID,Insertion Order Status,Insertion Order Integration Code,Line Item,Line Item ID,Line Item Status,Line Item Integration Code,Targeted Data Providers,Cookie Reach: Average Impression Frequency,Cookie Reach: Impression Reach",
        test_string_to_encode.encode("utf-8"),
        test_string_to_encode.encode("ascii"),
        test_string_to_encode.encode("windows-1252"),
        test_string_to_encode.encode("latin_1"),
    ]
    line_iterator_multiple_encodings = (line for line in lines)
    expected_dict = {
        "Country": "BR",
        "Partner": "Sanofi Aventis Brasil",
        "Partner ID": "3945535",
        "Partner Status": "Active",
        "Advertiser": "Allegra",
        "Advertiser ID": "3992233",
        "Advertiser Status": "0",
        "Advertiser Integration Code": "",
        "Insertion Order": "YR_Sanofi_Allegra_201910_Consideration_DV360_Precision_Native-Ads_Cross-Device_BR",
        "Insertion Order ID": "11140383",
        "Insertion Order Status": "Active",
        "Insertion Order Integration Code": "",
        "Line Item": "YR_Sanofi_Allegra_201910_Consideration_DV360_Precision_OA_Native-Ads_DV-Affinity-Health_Desktop_BR",
        "Line Item ID": "1130016",
        "Line Item Status": "0",
        "Line Item Integration Code": "",
        "Targeted Data Providers": '"    "',
        "Cookie Reach: Average Impression Frequency": "0.00",
        "Cookie Reach: Impression Reach": "4080863",
    }
    for yielded_dict in get_generator_dict_from_str_csv(
        line_iterator_multiple_encodings
    ):
        assert yielded_dict == expected_dict


def test_blank_line():
    lines = [
        b"Country,Partner,Partner ID,Partner Status,Advertiser,Advertiser ID,Advertiser Status,Advertiser Integration Code,Insertion Order,Insertion Order ID,Insertion Order Status,Insertion Order Integration Code,Line Item,Line Item ID,Line Item Status,Line Item Integration Code,Targeted Data Providers,Cookie Reach: Average Impression Frequency,Cookie Reach: Impression Reach",
        ""
    ]
    line_iterator_with_blank_line = (line for line in lines)
    assert get_generator_dict_from_str_csv(
        line_iterator_with_blank_line
    )

    lines.insert(1, b'BR,Sanofi Aventis Brasil,3945535,Active,Allegra,3992233,0,,YR_Sanofi_Awareness_2019_Allegra_Hardsell_Display_DV360_Cross-Device_BR,8674464,Active,,YR_Sanofi_Allegra_Hardsell_Display_Datalogix-Health-Beauty-Buyers-Allergy_Desktop_BR,26143278,0,,"",0.00,41')
    expected_dict = {
        "Country": "BR",
        "Partner": "Sanofi Aventis Brasil",
        "Partner ID": "3945535",
        "Partner Status": "Active",
        "Advertiser": "Allegra",
        "Advertiser ID": "3992233",
        "Advertiser Status": "0",
        "Advertiser Integration Code": "",
        "Insertion Order": "YR_Sanofi_Awareness_2019_Allegra_Hardsell_Display_DV360_Cross-Device_BR",
        "Insertion Order ID": "8674464",
        "Insertion Order Status": "Active",
        "Insertion Order Integration Code": "",
        "Line Item": "YR_Sanofi_Allegra_Hardsell_Display_Datalogix-Health-Beauty-Buyers-Allergy_Desktop_BR",
        "Line Item ID": "26143278",
        "Line Item Status": "0",
        "Line Item Integration Code": "",
        "Targeted Data Providers": '""',
        "Cookie Reach: Average Impression Frequency": "0.00",
        "Cookie Reach: Impression Reach": "41",
    }
    line_iterator_with_blank_line = (line for line in lines)
    for dic in get_generator_dict_from_str_csv(
        line_iterator_with_blank_line
    ):
        assert dic == expected_dict

    lines.append("This is something that should not be here.")
    line_iterator_with_blank_line = (line for line in lines)
    test_result = get_generator_dict_from_str_csv(
        line_iterator_with_blank_line
    )
    assert len(list(test_result)) == 1
    for dic in test_result:
        assert dic == expected_dict


def test_invalid_byte():
    lines = [
        b"Country,Partner,Partner ID,Partner Status,Advertiser,Advertiser ID,Advertiser Status,Advertiser Integration Code,Insertion Order,Insertion Order ID,Insertion Order Status,Insertion Order Integration Code,Line Item,Line Item ID,Line Item Status,Line Item Integration Code,Targeted Data Providers,Cookie Reach: Average Impression Frequency,Cookie Reach: Impression Reach",
        b'BR,Sanofi Aventis Brasil,3945535,Active,Allegra,3992233,0,,YR_Sanofi_Awareness_2019_Allegra_Hardsell_Display_DV360_Cross-Device_BR,8674464,Active,,YR_Sanofi_Allegra_Hardsell_Display_Datalogix-Health-Beauty-Buyers-Allergy_Desktop_BR,26143278,0,,"   \x91\xea\xd0$",0.00,41',
    ]
    line_iterator_invalid_byte = (line for line in lines)
    expected_dict = {
        "Country": "BR",
        "Partner": "Sanofi Aventis Brasil",
        "Partner ID": "3945535",
        "Partner Status": "Active",
        "Advertiser": "Allegra",
        "Advertiser ID": "3992233",
        "Advertiser Status": "0",
        "Advertiser Integration Code": "",
        "Insertion Order": "YR_Sanofi_Awareness_2019_Allegra_Hardsell_Display_DV360_Cross-Device_BR",
        "Insertion Order ID": "8674464",
        "Insertion Order Status": "Active",
        "Insertion Order Integration Code": "",
        "Line Item": "YR_Sanofi_Allegra_Hardsell_Display_Datalogix-Health-Beauty-Buyers-Allergy_Desktop_BR",
        "Line Item ID": "26143278",
        "Line Item Status": "0",
        "Line Item Integration Code": "",
        "Targeted Data Providers": '"   $"',
        "Cookie Reach: Average Impression Frequency": "0.00",
        "Cookie Reach: Impression Reach": "41",
    }
    for yielded_dict in get_generator_dict_from_str_csv(
        line_iterator_invalid_byte
    ):
        assert yielded_dict == expected_dict
