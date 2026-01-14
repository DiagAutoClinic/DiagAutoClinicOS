# create_fix.py
import os

# Read the original models.py
with open('src/vin/models.py', 'r') as f:
    models_lines = f.readlines()

# Find the EpistemologicalValue class
new_models_lines = []
in_class = False
replaced = False
i = 0

while i < len(models_lines):
    line = models_lines[i]
    
    if 'class EpistemologicalValue:' in line and '@dataclass' in models_lines[i-1]:
        # Found the class - replace it
        new_models_lines.append('@dataclass\n')
        new_models_lines.append('class EpistemologicalValue:\n')
        new_models_lines.append('    """\n')
        new_models_lines.append('    A value that is NEVER naked — always carries epistemology.\n')
        new_models_lines.append('    This is the core building block of the entire system.\n')
        new_models_lines.append('    """\n')
        new_models_lines.append('    value: Any\n')
        new_models_lines.append('    status: EpistemologicalStatus\n')
        new_models_lines.append('    confidence: float\n')
        new_models_lines.append('    unit: Optional[str] = None\n')
        new_models_lines.append('    sources: List[FieldSource] = field(default_factory=list)\n')
        new_models_lines.append('    explanation: Optional[str] = None\n')
        new_models_lines.append('    conflicts: List[str] = field(default_factory=list)\n')
        new_models_lines.append('\n')
        new_models_lines.append('    @property\n')
        new_models_lines.append('    def is_reliable(self) -> bool:\n')
        new_models_lines.append('        """Quick helper: should this value be trusted for decisions?"""\n')
        new_models_lines.append('        return self.status in (EpistemologicalStatus.VERIFIED, EpistemologicalStatus.CONFIRMED) \\\n')
        new_models_lines.append('               and self.confidence >= 0.90\n')
        new_models_lines.append('\n')
        new_models_lines.append('    def add_source(self, source: FieldSource):\n')
        new_models_lines.append('        """Append a new contributing source and update confidence/status if needed"""\n')
        new_models_lines.append('        self.sources.append(source)\n')
        new_models_lines.append('        # Naive aggregation example — can be made much smarter later\n')
        new_models_lines.append('        self.confidence = max(s.confidence for s in self.sources) if self.sources else 0.0\n')
        
        # Skip the old class definition
        # Find where the old class ends (look for next empty line or class definition)
        i += 1
        while i < len(models_lines) and not models_lines[i].strip().startswith(('class ', 'def ', '@')):
            i += 1
        replaced = True
        continue
    else:
        new_models_lines.append(line)
        i += 1

# Write fixed models.py
with open('src/vin/models.py', 'w') as f:
    f.writelines(new_models_lines)

print("Fixed models.py")

# Now fix layer2_oem_grammar.py
with open('src/vin/layer2_oem_grammar.py', 'r') as f:
    layer2_lines = f.readlines()

# Fix indentation for load_rules method
new_layer2_lines = []
i = 0

while i < len(layer2_lines):
    line = layer2_lines[i]
    
    if 'def load_rules(self, path: Union[str, Path]):' in line:
        # Found the method - ensure proper indentation
        new_layer2_lines.append(line)
        i += 1
        
        # The next line should be properly indented
        while i < len(layer2_lines) and layer2_lines[i].strip() != '':
            # Ensure 4 spaces of indentation
            if not layer2_lines[i].startswith(' ' * 4):
                new_layer2_lines.append(' ' * 4 + layer2_lines[i].lstrip())
            else:
                new_layer2_lines.append(layer2_lines[i])
            i += 1
        
        # Add the empty line
        if i < len(layer2_lines):
            new_layer2_lines.append(layer2_lines[i])
            i += 1
    else:
        new_layer2_lines.append(line)
        i += 1

# Write fixed layer2_oem_grammar.py
with open('src/vin/layer2_oem_grammar.py', 'w') as f:
    f.writelines(new_layer2_lines)

print("Fixed layer2_oem_grammar.py")
print("\nNow run: pytest src/tests/ -v")