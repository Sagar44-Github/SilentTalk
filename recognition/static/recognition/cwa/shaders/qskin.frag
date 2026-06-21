// qskin.frag
// Fragment shader.  Basic Phong-ish lighting.

#ifdef GL_ES
	precision highp float;
#endif

//========  Fragment shader input (from vertex shader).  ========

varying vec3 Normal;
varying vec2 TexCoord0;


//========  Uniforms.  ========

uniform sampler2D TexSampler0;
uniform vec4 Colour;


//========  main()  ========

void main(void)
{
	// Ambient/diffuse light calculation.
	vec3 lightDir = normalize(vec3(0.3, 0.5, 1.0));
	vec3 norm = normalize(Normal);
	float lightFactor = max(dot(norm, lightDir), 0.0);
	float ambient = 0.3;
	float diffuse = 0.7 * lightFactor;
	float intensity = ambient + diffuse;

	vec4 texColour = texture2D(TexSampler0, TexCoord0);
	if (texColour.a > 0.01) {
		gl_FragColor = vec4(intensity * texColour.rgb, texColour.a);
	} else {
		gl_FragColor = vec4(intensity * Colour.rgb, Colour.a);
	}
}
