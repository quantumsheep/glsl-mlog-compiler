# GLSL to mlog compiler
Transpiles GLSL to [mlog](https://mindustrygame.github.io/wiki/logic/0-introduction/).

# Example
```glsl
void main() {
  vec2 st = gl_FragCoord.xy / u_resolution.xy;
  gl_FragColor = vec4(atan(st.y, st.x), sin(st.y), cos(st.x), 1.0);
}
```
![Example 1](https://i.imgur.com/ZVw7w8X.png)

# How to use
```shell
python3 . example.glsl
```
