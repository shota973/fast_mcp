# 参考 https://flet.dev/docs/tutorials/python-chat

import flet as ft
import time
import langchain_client
import model
from langchain_mcp_adapters.client import MultiServerMCPClient

class Message:
    def __init__(self, user_name: str, text: str, message_type: str):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type


class ChatMessage(ft.Row):
    def __init__(self, message: Message):
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(self.get_initials(message.user_name)),
                color=ft.Colors.WHITE,
                bgcolor=self.get_avatar_color(message.user_name),
            ),
            ft.Column(
                [
                    ft.Text(message.user_name, weight="bold"),
                    ft.Text(message.text, selectable=True),
                ],
                tight=True,
                spacing=5,
            ),
        ]

    def get_initials(self, user_name: str):
        if user_name:
            return user_name[:1].capitalize()
        else:
            return "Unknown"  # or any default value you prefer

    def get_avatar_color(self, user_name: str):
        colors_lookup = [
            ft.Colors.AMBER,
            ft.Colors.BLUE,
            ft.Colors.BROWN,
            ft.Colors.CYAN,
            ft.Colors.GREEN,
            ft.Colors.INDIGO,
            ft.Colors.LIME,
            ft.Colors.ORANGE,
            ft.Colors.PINK,
            ft.Colors.PURPLE,
            ft.Colors.RED,
            ft.Colors.TEAL,
            ft.Colors.YELLOW,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]


async def main(page: ft.Page):
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.title = "AI Chat"

    agent = await langchain_client.create_client()
    async def send_message_click(e):
        if new_message.value != "":
            add_message(
                Message(
                    "user",
                    new_message.value,
                    message_type="chat_message",
                )
            )
            time.sleep(0.2) # delayがあったほうが見やすかったのでdelayをかけた
            loading_message = add_message(
                Message(
                    model.CHAT_MODEL,
                    "Loading...",
                    message_type="chat_message",
                )
            )
            answers = await langchain_client.send_message(agent, new_message.value)
            chat.controls.remove(loading_message)
            for answer in answers:
                add_message(
                    Message(
                        answer[0],
                        answer[1],
                        message_type="chat_message",
                    )
                )
            new_message.value = ""
            new_message.focus()
            page.update()

    def add_message(message: Message) -> ChatMessage:
        m = ChatMessage(message)
        chat.controls.append(m)
        page.update()
        return m

    # Chat messages
    chat = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    # A new message entry form
    new_message = ft.TextField(
        hint_text="Write a message...",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        on_submit=send_message_click,
    )

    # Add everything to the page
    page.add(
        ft.Container(
            content=chat,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=5,
            padding=10,
            expand=True,
        ),
        ft.Row(
            [
                new_message,
                ft.IconButton(
                    icon=ft.Icons.SEND_ROUNDED,
                    tooltip="Send message",
                    on_click=send_message_click,
                ),
            ]
        ),
    )

if __name__ == "__main__":
    ft.app(target=main)
