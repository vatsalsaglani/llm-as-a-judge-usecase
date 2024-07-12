## defining function schemas

from typing import Union, Literal
from pydantic import BaseModel, Field


# NonToolAnswer schema will be used for verifying the output
class NonToolAnswer(BaseModel):
    answer: str


avaialle_non_tool_answering = [{
    "name": "Answer",
    "description": "Answer the user message without being verbose.",
    "parameters": NonToolAnswer.model_json_schema()
}]

function_names = [
    "Answer", "MakeCall", "CallInteraction", "SendMessage", "AudioInteraction",
    "MapInteraction"
]


class SearchTool(BaseModel):
    q: str = Field(..., description="Search Query.")


class UseContact(BaseModel):
    is_number: bool = Field(
        ...,
        description=
        "True if a number is specified by the user and False if the user provides contact name."
    )
    number: Union[str, None] = Field(
        ..., description="The number if provided by the user else None.")
    contact_name: Union[str, None] = Field(
        ...,
        description=
        "If a number is not provided the user will provide the name of the contact to call."
    )


class MakeCall(BaseModel):
    app_name: Literal["Phone", "WhatsApp"] = Field(
        default="Phone",
        description="Specify the application name provided by the user.")
    meta: UseContact


class CallInteraction(BaseModel):
    interaction_type: Literal["ACCEPT", "REJECT"] = Field(
        ..., description="The user can ask to accept or reject the call.")


class SendMessage(BaseModel):
    app_name: Literal["Phone", "WhatsApp"] = Field(
        default="Phone",
        description="Specify the application name provided by the user.")
    meta: UseContact
    message_text: str = Field(
        ..., description="The message the user wants to send.")


class AudioInteraction(BaseModel):
    action: Literal["Select", "Play", "Pause"] = Field(
        ...,
        description=
        "The user can either select a song to play, pause a song, or play a paused song"
    )
    is_select: bool = Field(
        ..., description="True if a user is asking to play a specific song.")
    song_name: Union[str, None] = Field(
        ...,
        description="Name of the song in case `is_select` is true else None.")


class Stop(BaseModel):
    action: Literal["Add", "Remove"] = Field(
        ..., description="The user can ask to add or remove a stop.")
    name: str = Field(..., description="Name of the stop.")


class MapInteraction(BaseModel):
    action: Literal["Start", "Update"] = Field(
        ...,
        description=
        "The user can start the map action by saying where they want to go. Or else they can provide an update to add or remove a stop."
    )
    is_update: bool = Field(
        ...,
        description=
        "If the user is asking to add or remove a stop then it's update.")
    stop: Union[Stop, None] = Field(
        ...,
        description=
        "The stop details are required if `is_update` is true else it can be None"
    )


available_domain_specific_tools = [{
    "name": "MakeCall",
    "description": "Used to make a call.",
    "parameters": MakeCall.model_json_schema()
}, {
    "name":
    "CallInteraction",
    "description":
    "Used to interact with an incoming call.",
    "parameters":
    CallInteraction.model_json_schema()
}, {
    "name":
    "SendMessage",
    "description":
    "Used to send a message.",
    "parameters":
    SendMessage.model_json_schema()
}, {
    "name":
    "AudioInteraction",
    "description":
    "Used to interact with audio system like select music, pause music, or play a paused music",
    "parameters":
    AudioInteraction.model_json_schema()
}, {
    "name":
    "MapInteraction",
    "description":
    "Used to set or update location in the map",
    "parameters":
    MapInteraction.model_json_schema()
}]

available_search_tool_functions = [{
    "name": "Search",
    "description": "Search for the user query",
    "parameters": SearchTool.model_json_schema()
}]
