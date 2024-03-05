# qGen

Software de monitorización y creación de Informes Formales con Polar H10

## Instalacion

Trabaja con Polar H10, version 5.0.0 o posterior
    
    python -m venv venv
    source venv/bin/activate  # On Windows, use `my_project_env\Scripts\activate`
    pip install -r requirements.txt
    python EBYT.py 

Integrar la aplicación con pyinstaller:

    pyinstaller EBYT.spec

Track each breath cycle in the top graph, and how heart rate oscillates in repsonse.

Adjust breathing pace and control to target the green zone of heart rate variability in the bottom graph (> 150 ms).

## Contributing
Feedback, bug reports, and pull requests are welcome. Feel free to submit an issue or create a pull request on GitHub.
