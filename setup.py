from setuptools import setup


setup(
    name="enabler",
    version="0.1.0",
    packages=["enabler", "src.enabler_keitaro_inc.commands", "src.enabler_keitaro_inc.helpers"], # noqa
    include_package_data=True,
    install_requires=["click==7.1.1",
                      "click-log==0.3.2",
                      "click-spinner==0.1.8",
                      "docker==4.2.0",
                      "gitpython==3.1.41",
                      "paramiko>=2.7.1",
                      "semver>=2.9.1",
                      "cryptography>=2.9.1",
                      "flake8>=7.0.0"],
    entry_points="""
        [console_scripts]
        enabler=src.enabler_keitaro_inc.enabler:cli
    """,
)
