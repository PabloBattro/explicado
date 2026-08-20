# explicado

Sitio de explicadores de conceptos. **Lo escribe César, un agente de software**, dirigido por
Pablo desde Telegram.

Existe para dos cosas a la vez: publicar cosas que valga la pena leer, y ser el primer
proyecto donde César llega hasta producción.

## Cómo se trabaja acá

- **Nadie pushea directo a `main`.** Todo entra por Pull Request. Lo hace cumplir GitHub, no
  la buena voluntad.
- **Un PR no se mergea con el CI en rojo.** También lo hace cumplir GitHub.
- Cada PR genera una URL de preview con el cambio aplicado. **Esa es la forma de revisar**:
  se mira la página, no el código.
- El merge a `main` publica. No hay paso intermedio.

## El CI

`scripts/verificar.py`, sin dependencias — solo la librería estándar de Python. Sobre cada
`.html` chequea que las etiquetas cierren donde corresponde, que haya `<title>` y `<h1>`, y
que los links a archivos del repo apunten a algo que exista.

No chequea links externos a propósito: dependen de que el servidor de otro esté vivo, y un CI
que falla por eso deja de ser una señal y pasa a ser ruido.

```bash
python3 scripts/verificar.py
```

## Lo que no va acá

Nada operativo del sistema de agentes: ni rutas, ni direcciones, ni nombres de credenciales.
Conceptos sí; el plano de una casa viva, no.
