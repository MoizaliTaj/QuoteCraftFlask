function convert_amount_to_words(number){
    function for_less_then_thousand(num_to_words){
        units_words = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", ]
        tens_words = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen", "Twenty"]
        tenss_words = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety", ]
        output = ""
        hundred_available = false;
        if (parseInt(num_to_words / 100) != 0){
            hundred_available = true
            output += units_words[parseInt(num_to_words / 100)] + " Hundred"
        }
        num_to_words = num_to_words % 100
        if (num_to_words > 9){
            if (num_to_words <= 20){
                if (hundred_available){
                    output += " And " + tens_words[num_to_words - 10]
                }
                else{
                    output += tens_words[num_to_words - 10]
                }
                
            } else {
                if ((num_to_words % 10) == 0){
                    if (hundred_available){
                        output += " and " + tenss_words[parseInt(num_to_words / 10)]
                    } else {
                        output += tenss_words[parseInt(num_to_words / 10)]
                    }
                    
                }
                else {
                    if (hundred_available){
                        output += " and " + tenss_words[parseInt(num_to_words / 10)] + "-" + units_words[num_to_words % 10]
                    } else {
                        output += tenss_words[parseInt(num_to_words / 10)] + "-" + units_words[num_to_words % 10]
                    }
                    
                }
                
            }
        }
        else if (num_to_words > 0) {
            if (hundred_available){
                output += " and " + units_words[num_to_words]
            } else {
                output += units_words[num_to_words]
            }
        }
        return output
    }
    if (number > 0.01){
        let outcome = "something"
        decimal_value = parseInt(((number % 1) * 100) + 0.001)
        under_thousand = parseInt(number % 1000)
        under_million = parseInt((number % 1000000) / 1000)
        above_million = parseInt(number / 1000000)
    }
    outcome = ""
    if (above_million > 0){
        outcome += "Dirham " + for_less_then_thousand(above_million) + " Million"
    }
    if (under_million > 0){
        if (above_million > 0){
            outcome += ", " + for_less_then_thousand(under_million) + " Thousand"
        } else {
            outcome += "Dirham " + for_less_then_thousand(under_million) + " Thousand"
        }
    }
    if (under_thousand > 0){
        if ((above_million > 0) || (under_million > 0)){
            if (under_thousand > 99){
                outcome += ", " + for_less_then_thousand(under_thousand)
            } else {
                outcome += " And " + for_less_then_thousand(under_thousand)
            }
        } else {
            outcome += "Dirham " + for_less_then_thousand(under_thousand)
        }
    }
    if (decimal_value > 0){
        if ((above_million > 0) || (under_million > 0) || (under_thousand > 0)){
            outcome += " And " + for_less_then_thousand(decimal_value) + ' Fils'
        } else {
            outcome += for_less_then_thousand(decimal_value) + " Fils"
        }

    }
    outcome += " Only"
    
    return outcome
}