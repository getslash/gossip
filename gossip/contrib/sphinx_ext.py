import gossip
from docutils import nodes, statemachine
from docutils.parsers import rst
from docutils.parsers.rst import directives
from sphinx.util import logging


_sphinx_log = logging.getLogger(__name__)
_INDENT_SIZE = 4


def _indent(text, level=1):
    indent_str = ' ' * (_INDENT_SIZE * level)
    return "".join(
        f'{indent_str if line.strip() else ""}{line}'
        for line in text.splitlines(True)
        )


def _yield_mutliple_values(title, values):
    if not values:
        return

    yield f"**{title}**"

    yield ""

    for value in values:
        yield _indent(value)
        yield ""

    yield ""


def _format_hook(hook):

    if hook.deprecated:
        yield "**DEPRECATED**"
        yield ""


    if hook.doc:
        for line in hook.doc.splitlines():
            yield line
        yield ""


    for val in _yield_mutliple_values("Tags", hook.tags):
        yield val


    for val in _yield_mutliple_values("Arguments", hook.get_argument_names()):
        yield val

    yield ""


class GossipDirective(rst.Directive):

    has_content = False
    required_arguments = 0
    option_spec = {
        "group_name": directives.unchanged_required,
    }


    def run(self):
        group_name = self.options.get("group_name")
        try:
            group = gossip.groups.get_group(group_name)
        except Exception as e:
            raise self.error(f"Could not retrieve :group_name: ({e!r})")

        sections = []
        source_name = group.full_name

        for hook in sorted(group.iter_hooks(recursive=True), key=lambda hook: hook.full_name):
            result = statemachine.ViewList()
            hook_section = nodes.section(
                '',
                nodes.title(text=hook.full_name),
                ids=[nodes.make_id(hook.full_name)],
                names=[nodes.fully_normalize_name(hook.full_name)])

            lines = _format_hook(hook)
            for line in lines:
                _sphinx_log.debug(line)
                result.append(line, source_name)
            sections.append(hook_section)
            self.state.nested_parse(result, 0, hook_section)

        return sections


def setup(app):
    app.add_directive("gossip", GossipDirective)
