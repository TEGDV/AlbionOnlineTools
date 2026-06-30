import re

with open('static/html/crafting_calculator.html', 'r') as f:
    content = f.read()

# Hide Tax% header
content = content.replace('<th class="py-2 px-2 font-medium text-center w-20">Tax%</th>', '<th class="py-2 px-2 font-medium text-center w-20 hidden">Tax%</th>')

# Hide Tax% data cell (Line 420)
# We need to find the <td class="py-3 px-1"> that contains x-model.number="item.sellTax"
tax_cell_pattern = r'(<td class="py-3 px-1">\s*<input type="number" x-model\.number="item\.sellTax".*?</td>)'
content = re.sub(tax_cell_pattern, lambda m: m.group(1).replace('<td class="py-3 px-1">', '<td class="py-3 px-1 hidden">'), content, flags=re.DOTALL)

# Adjust widths of monetary fields in headers
content = content.replace('<th class="py-2 px-2 font-medium text-center w-28">Sell Price</th>', '<th class="py-2 px-2 font-medium text-center w-36">Sell Price</th>')
content = content.replace('<th class="py-2 px-2 font-medium text-right w-32">Craft Cost</th>', '<th class="py-2 px-2 font-medium text-right w-36">Craft Cost</th>')
content = content.replace('<th class="py-2 px-2 font-medium text-right w-32">Profit</th>', '<th class="py-2 px-2 font-medium text-right w-36">Profit</th>')
content = content.replace('<th class="py-2 px-2 font-medium text-right w-32">Total</th>', '<th class="py-2 px-2 font-medium text-right w-36">Total</th>')

# Add whitespace-nowrap to all right-aligned text cells (monetary values)
content = content.replace('<td class="py-3 px-2 text-right">', '<td class="py-3 px-2 text-right whitespace-nowrap">')
content = content.replace('<td class="py-3 px-2 text-right font-medium">', '<td class="py-3 px-2 text-right font-medium whitespace-nowrap">')

# Modify the City Dropdown button
# Remove text
content = content.replace('<span class="truncate text-zinc-300" x-text="item.sellCity || \'City\'"></span>', '')
# Make header smaller and centered
content = content.replace('<th class="py-2 px-2 font-medium w-36">City</th>', '<th class="py-2 px-2 font-medium w-14 text-center">City</th>')
# Center the dot in the button
# find: class="flex items-center space-x-2 overflow-hidden" -> class="flex items-center justify-center w-full"
content = content.replace('<div class="flex items-center space-x-2 overflow-hidden">', '<div class="flex items-center justify-center w-full">')
# the chevron svg
# we can hide the chevron or leave it. The user said "unicamente deja el punto de color". I'll remove the svg too.
content = re.sub(r'<svg class="w-3 h-3 text-zinc-500 shrink-0".*?</svg>', '', content)
# the button itself had flex justify-between
content = content.replace('flex justify-between items-center', 'flex justify-center items-center')

with open('static/html/crafting_calculator.html', 'w') as f:
    f.write(content)

print("UI fixes applied")
