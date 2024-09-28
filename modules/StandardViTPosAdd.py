# © 2024 Alec Fessler
# MIT License
# See LICENSE file in the project root for full license information.

import torch
import torch.nn as nn
from modules.PatchEmbed import PatchEmbed
from modules.SelfAttn import SelfAttn

class StandardViTPosAdd(nn.Module):
    def __init__(
        self,
        img_size=32,
        patch_size=8,
        in_channels=3,
        attn_embed_dim=256,
        attn_heads=4,
        num_transformer_layers=6,
        stochastic_depth=0.1
    ):
        super(StandardViTPosAdd, self).__init__()
        self.patch_embed = PatchEmbed(
            patch_size=patch_size,
            in_channels=in_channels,
            embed_dim=attn_embed_dim
        )

        self.pos_embeds = nn.Parameter(torch.randn(1, (img_size // patch_size) ** 2, attn_embed_dim))

        self.cls_token = nn.Parameter(torch.randn(1, 1, attn_embed_dim))

        self.transformer_layers = nn.ModuleList([
            SelfAttn(embed_dim=attn_embed_dim, num_heads=attn_heads, stochastic_depth=stochastic_depth)
            for _ in range(num_transformer_layers)
        ])

        self.norm = nn.LayerNorm(attn_embed_dim)
        self.fc = nn.Linear(attn_embed_dim, 10)

    def forward(self, x):
        x = self.patch_embed(x)
        x += self.pos_embeds
        cls_tokens = self.cls_token.expand(x.size(0), -1, -1)
        x = torch.cat((cls_tokens, x), dim=1)
        x = x.permute(1, 0, 2).contiguous()
        for layer in self.transformer_layers:
            x = layer(x)
        x = x[0]
        x = self.norm(x)
        x = self.fc(x)
        return x
