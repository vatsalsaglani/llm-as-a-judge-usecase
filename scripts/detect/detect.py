from mitigate.schemas import *
from pydantic import ValidationError


def verifyFunctionNameAndSchema(function_call_output):
    name2validation = {
        "CallInteraction":
        lambda fco: CallInteraction.model_validate(fco.get("parameters")),
        "Answer":
        lambda fco: NonToolAnswer.model_validate(fco.get("parameters")),
        "MakeCall":
        lambda fco: MakeCall.model_validate(fco.get('parameters')),
        "SendMessage":
        lambda fco: SendMessage.model_validate(fco.get("parameters")),
        "AudioInteraction":
        lambda fco: AudioInteraction.model_validate(fco.get("parameters")),
        "MapInteraction":
        lambda fco: MapInteraction.model_validate(fco.get("parameters"))
    }
    if function_call_output.get('name') in name2validation:
        try:
            name2validation[function_call_output.get("name")](
                function_call_output)
            return True, ""
        except ValidationError as err:
            return False, str(err)
    else:
        return False, "Function Call Not Available!"
