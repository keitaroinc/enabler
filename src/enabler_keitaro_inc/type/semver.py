from semver import parse
import click


class BasedVersionParamType(click.ParamType):
    name = "semver"

    def convert(self, value, param, ctx):
        try:
            parse(value)
            return value
        except (TypeError, ValueError):
            parts = value.split('.')
            if len(parts) == 2:
                parts.append('0')  # Default patch version to 0 if not provided
            elif len(parts) == 3:
                # Increment patch version for bug fixes
                parts[2] = str(int(parts[2]) + 1)
            else:
                self.fail(f'{value!r} is not a valid version, please use semver', param, ctx) # noqa

            return '.'.join(parts)
