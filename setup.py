import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
	long_description = fh.read()

setuptools.setup(
		name="WeatherUnits",
		version="0.4",
		license='MIT license',
		author="noblecloud",
		author_email="git@noblecloud.io",
		description="Easy conversion for common weather units",
		long_description=long_description,
		long_description_content_type="text/markdown",
		url="https://github.com/noblecloud/WeatherUnits",
		project_urls={
				"Bug Tracker": "https://github.com/noblecloud/WeatherUnits/issues",
		},
		classifiers=[
				"Programming Language :: Python :: 3.9",
				"License :: OSI Approved :: MIT License",
				"Operating System :: OS Independent",
				"Natural Language :: English",
				"Development Status :: 4 - Beta",
				"Topic :: Utilities",
				"Topic :: Scientific/Engineering :: Atmospheric Science"
		],
		package_dir={"": "src"},
		package_data={
			'': ['*.ini'],
		},
		packages=setuptools.find_packages(where="src"),
		python_requires=">=3.7",
)
