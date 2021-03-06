float clamp(float f, float a, float b) {
    return min(max(f, a), b);
}

float distance(vec2 p1, vec2 p2) {
    float a = p2.x - p1.x;
    float b = p2.y - p1.y;
    return sqrt((a * a) + (b * b));
}

float length(float f) {
    return sqrt((f * f) + (f * f));
}

float step(float edge, float x) {
    if(x < edge) {
        return 0.0;
    }

    return 1.0;
}

float smoothstep(float edge0, float edge1, float x) {
    x = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0);
    return x * x * (3.0 - 2.0 * x);
}

float dot(vec2 a, vec2 b) {
    return a.x * b.x + a.y * b.y;
}

float abs(float value) {
    if(value < 0) {
        return -value;
    }

    return value;
}

vec2 abs(vec2 p) {
    return vec2(length(p.x), length(p.y));
}

vec2 floor(vec2 p) {
    return vec2(floor(p.x), floor(p.y));
}

float fract(float x) {
    return x - floor(x);
}

vec2 fract(vec2 x) {
    return x - floor(x);
}

float mod(float x, float y) {
    return x - y * floor(x / y);
}

vec2 mod(vec2 x, vec2 y) {
    return x - y * floor(x / y);
}

vec2 mod(vec2 x, float y) {
    return x - y * floor(x / y);
}

float atan(float y, float x) {
    if(x > 0.0) {
        return atan(y / x);
    } else if(x < 0.0) {
        if(y >= 0.0) {
            return atan(y / x) + 3.1415926538;
        } else if(y < 0.0) {
            return atan(y / x) - 3.1415926538;
        }
    } else if(x == 0.0) {
        if(y > 0.0) {
            return 3.1415926538 / 2.0;
        } else if(y == 0.0) {
            return -(3.1415926538 / 2.0);
        }
    }

    return 0.0;
}

float atan(vec2 p) {
    return atan(p.x, p.y);
}
