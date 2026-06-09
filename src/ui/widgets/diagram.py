import pygame
from src.ui.theme import theme

class BlockDiagram:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.scale = 1.0

    def draw(self, surface, module_name, ports):
        pygame.draw.rect(surface, theme.colors["sideBar.background"], self.rect, border_radius=12)
        pygame.draw.rect(surface, theme.colors["sideBar.border"], self.rect, width=2, border_radius=12)

        if not module_name:
            module_name = "unnamed_module"

        inputs = [p for p in ports if p["dir"] == "IN"]
        outputs = [p for p in ports if p["dir"] == "OUT"]

        # Calculate responsive sizes based on scaling
        block_w = int(260 * self.scale)
        v_spacing = int(36 * self.scale)
        block_h = max(int(180 * self.scale), max(len(inputs), len(outputs)) * v_spacing + int(60 * self.scale))
        
        block_x = self.rect.x + (self.rect.width - block_w) // 2
        block_y = self.rect.y + (self.rect.height - block_h) // 2

        # Create scaled fonts for diagram text
        font_sz = max(8, int(14 * self.scale))
        title_sz = max(10, int(16 * self.scale))
        small_sz = max(6, int(10 * self.scale))
        
        # Load standard system font dynamically based on size
        font = pygame.font.SysFont(theme.sans_name, font_sz)
        font_bold = pygame.font.SysFont(theme.sans_name, title_sz, bold=True)
        font_small = pygame.font.SysFont(theme.sans_name, small_sz)

        # Inputs (Left side)
        for i, port in enumerate(inputs):
            name = port["name"] or "unnamed"
            width = port["width"] or "1"
            py = block_y + int(40 * self.scale) + i * v_spacing
            
            line_x1 = self.rect.x + 30
            line_x2 = block_x
            
            color = theme.colors["ports.input"]
            icon_type = None
            if name.lower() in ["clk", "clock", "i_clk"]:
                color = theme.colors["ports.clock"]
                icon_type = "clk"
            elif name.lower() in ["rst", "reset", "rst_n", "i_rst", "rst_b"]:
                color = theme.colors["ports.reset"]
                icon_type = "rst"

            pygame.draw.line(surface, color, (line_x1, py), (line_x2, py), 2)
            pygame.draw.polygon(surface, color, [
                (block_x - 6, py - 4),
                (block_x, py),
                (block_x - 6, py + 4)
            ])

            if icon_type == "clk":
                pygame.draw.lines(surface, color, False, [
                    (line_x1 + 5, py + 4),
                    (line_x1 + 10, py + 4),
                    (line_x1 + 10, py - 4),
                    (line_x1 + 15, py - 4),
                    (line_x1 + 15, py + 4),
                    (line_x1 + 20, py + 4)
                ], 1)
            elif icon_type == "rst":
                pygame.draw.circle(surface, color, (line_x1 + 12, py), 4, 1)
                pygame.draw.line(surface, color, (line_x1 + 12, py - 4), (line_x1 + 12, py), 1)

            lbl = f"{name} [{width}]" if width != "1" else name
            lbl_surf = font.render(lbl, True, theme.colors["editor.foreground"])
            surface.blit(lbl_surf, (line_x1 + 25, py - lbl_surf.get_height() - 2))

        # Outputs (Right side)
        for i, port in enumerate(outputs):
            name = port["name"] or "unnamed"
            width = port["width"] or "1"
            py = block_y + int(40 * self.scale) + i * v_spacing
            
            line_x1 = block_x + block_w
            line_x2 = self.rect.right - 30
            
            color = theme.colors["ports.output"]
            pygame.draw.line(surface, color, (line_x1, py), (line_x2, py), 2)
            pygame.draw.polygon(surface, color, [
                (line_x2 - 6, py - 4),
                (line_x2, py),
                (line_x2 - 6, py + 4)
            ])

            lbl = f"{name} [{width}]" if width != "1" else name
            lbl_surf = font.render(lbl, True, theme.colors["editor.foreground"])
            surface.blit(lbl_surf, (line_x2 - lbl_surf.get_width() - 8, py - lbl_surf.get_height() - 2))

        # Central block
        block_rect = pygame.Rect(block_x, block_y, block_w, block_h)
        bg_surface = pygame.Surface((block_w, block_h), pygame.SRCALPHA)
        base_color = theme.colors["editor.background"]
        bg_surface.fill((base_color[0], base_color[1], base_color[2], 220))
        surface.blit(bg_surface, block_rect)
        
        pygame.draw.rect(surface, theme.colors["sideBar.border"], block_rect, width=2, border_radius=8)

        mod_lbl = font_bold.render(module_name, True, theme.colors["syntax.name"])
        surface.blit(mod_lbl, (block_x + (block_w - mod_lbl.get_width())//2, block_y + int(12 * self.scale)))
        
        sub_lbl = font_small.render("SYSTEMVERILOG MODULE", True, theme.colors["syntax.comment"])
        surface.blit(sub_lbl, (block_x + (block_w - sub_lbl.get_width())//2, block_y + int(12 * self.scale) + mod_lbl.get_height()))
