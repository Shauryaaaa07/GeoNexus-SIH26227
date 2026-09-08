import { useEffect, useRef } from "react"
import logo from "./assets/geonexus-logo.png"
import earth from "./assets/geonexus-earth.png"
import satellite from "./assets/geonexus-satellite.png"
import EarthChangesSection from "./components/EarthChangesSection";
import Process from "./components/Process";
import Section04 from "./components/Section04";
import Section05 from "./components/Section05";
import Section06 from "./components/Section06.jsx";
import Map from "./Map";
import "./App.css";

function App() {

  const starCanvasRef = useRef(null)

  /* =========================
     WEBGL STARFIELD
  ========================= */

  useEffect(() => {

    const canvas = starCanvasRef.current

    if (!canvas) return

    const gl =
      canvas.getContext("webgl", {
        alpha: true,
        antialias: false
      })

    if (!gl) {

      console.warn(
        "WebGL is not available in this browser."
      )

      return

    }


    /* =========================
       STAR CONFIGURATION
    ========================= */

    const STAR_COUNT = 1800

    const INTERACTION_RADIUS = 150

    const REPULSION_STRENGTH = 42

    const RETURN_SPEED = 0.055


    /* =========================
       STAR DATA
    ========================= */

    const stars = []

    for (let i = 0; i < STAR_COUNT; i++) {

      const depth =
        0.25 + Math.random() * 0.75

      const size =
        0.55 +
        Math.random() * 1.65

      const brightness =
        0.25 +
        Math.random() * 0.75

      const x =
        Math.random()

      const y =
        Math.random()

      stars.push({

        baseX: x,
        baseY: y,

        x,
        y,

        velocityX: 0,
        velocityY: 0,

        depth,

        size,

        brightness

      })

    }


    /* =========================
       WEBGL SHADERS
    ========================= */

    const vertexShaderSource = `

      attribute vec2 a_position;
      attribute float a_size;
      attribute float a_brightness;

      varying float v_brightness;

      void main() {

        gl_Position =
          vec4(
            a_position,
            0.0,
            1.0
          );

        gl_PointSize =
          a_size;

        v_brightness =
          a_brightness;

      }

    `


    const fragmentShaderSource = `

      precision mediump float;

      varying float v_brightness;

      void main() {

        vec2 point =
          gl_PointCoord -
          vec2(0.5);

        float distanceFromCenter =
          length(point);

        float alpha =
          smoothstep(
            0.5,
            0.05,
            distanceFromCenter
          );

        gl_FragColor =
          vec4(
            0.72,
            0.90,
            1.0,
            alpha * v_brightness
          );

      }

    `


    /* =========================
       SHADER CREATION
    ========================= */

    const createShader = (
      type,
      source
    ) => {

      const shader =
        gl.createShader(type)

      gl.shaderSource(
        shader,
        source
      )

      gl.compileShader(shader)


      if (
        !gl.getShaderParameter(
          shader,
          gl.COMPILE_STATUS
        )
      ) {

        console.error(
          gl.getShaderInfoLog(shader)
        )

        gl.deleteShader(shader)

        return null

      }

      return shader

    }


    const vertexShader =
      createShader(
        gl.VERTEX_SHADER,
        vertexShaderSource
      )


    const fragmentShader =
      createShader(
        gl.FRAGMENT_SHADER,
        fragmentShaderSource
      )


    if (
      !vertexShader ||
      !fragmentShader
    ) {
      return
    }


    /* =========================
       WEBGL PROGRAM
    ========================= */

    const program =
      gl.createProgram()

    gl.attachShader(
      program,
      vertexShader
    )

    gl.attachShader(
      program,
      fragmentShader
    )

    gl.linkProgram(program)


    if (
      !gl.getProgramParameter(
        program,
        gl.LINK_STATUS
      )
    ) {

      console.error(
        gl.getProgramInfoLog(program)
      )

      return

    }


    gl.useProgram(program)


    /* =========================
       BUFFER CREATION
    ========================= */

    const positionBuffer =
      gl.createBuffer()

    const sizeBuffer =
      gl.createBuffer()

    const brightnessBuffer =
      gl.createBuffer()


    /* =========================
       ATTRIBUTE LOCATIONS
    ========================= */

    const positionLocation =
      gl.getAttribLocation(
        program,
        "a_position"
      )

    const sizeLocation =
      gl.getAttribLocation(
        program,
        "a_size"
      )

    const brightnessLocation =
      gl.getAttribLocation(
        program,
        "a_brightness"
      )


    /* =========================
       STAR ARRAYS
    ========================= */

    const positions =
      new Float32Array(
        STAR_COUNT * 2
      )

    const sizes =
      new Float32Array(
        STAR_COUNT
      )

    const brightness =
      new Float32Array(
        STAR_COUNT
      )


    /* =========================
       INITIAL STAR VALUES
    ========================= */

    stars.forEach(
      (star, index) => {

        positions[index * 2] =
          star.x * 2 - 1

        positions[index * 2 + 1] =
          -(star.y * 2 - 1)

        sizes[index] =
          star.size

        brightness[index] =
          star.brightness

      }
    )


    /* =========================
       UPLOAD SIZE BUFFER
    ========================= */

    gl.bindBuffer(
      gl.ARRAY_BUFFER,
      sizeBuffer
    )

    gl.bufferData(
      gl.ARRAY_BUFFER,
      sizes,
      gl.STATIC_DRAW
    )


    gl.enableVertexAttribArray(
      sizeLocation
    )

    gl.vertexAttribPointer(
      sizeLocation,
      1,
      gl.FLOAT,
      false,
      0,
      0
    )


    /* =========================
       UPLOAD BRIGHTNESS BUFFER
    ========================= */

    gl.bindBuffer(
      gl.ARRAY_BUFFER,
      brightnessBuffer
    )

    gl.bufferData(
      gl.ARRAY_BUFFER,
      brightness,
      gl.STATIC_DRAW
    )


    gl.enableVertexAttribArray(
      brightnessLocation
    )

    gl.vertexAttribPointer(
      brightnessLocation,
      1,
      gl.FLOAT,
      false,
      0,
      0
    )


    /* =========================
       MOUSE POSITION
    ========================= */

    const mouse = {

      x: -1000,
      y: -1000

    }


    const handleMouseMove =
      (event) => {

        const rect =
          canvas.getBoundingClientRect()

        mouse.x =
          event.clientX -
          rect.left

        mouse.y =
          event.clientY -
          rect.top

      }


    const handleMouseLeave =
      () => {

        mouse.x = -1000

        mouse.y = -1000

      }


    window.addEventListener(
      "mousemove",
      handleMouseMove
    )

    window.addEventListener(
      "mouseleave",
      handleMouseLeave
    )


    /* =========================
       CANVAS RESIZE
    ========================= */

    const resizeCanvas =
      () => {

        const rect =
          canvas.getBoundingClientRect()

        const dpr =
          Math.min(
            window.devicePixelRatio || 1,
            1.75
          )

        canvas.width =
          rect.width * dpr

        canvas.height =
          rect.height * dpr

        gl.viewport(
          0,
          0,
          canvas.width,
          canvas.height
        )

      }


    resizeCanvas()

    window.addEventListener(
      "resize",
      resizeCanvas
    )


    /* =========================
       ANIMATION
    ========================= */

    let animationFrame


    const animate = () => {

      const width =
        canvas.clientWidth

      const height =
        canvas.clientHeight


      /* =========================
         UPDATE STAR POSITIONS
      ========================= */

      stars.forEach(
        (star, index) => {

          const starPixelX =
            star.x * width

          const starPixelY =
            star.y * height


          const dx =
            starPixelX -
            mouse.x

          const dy =
            starPixelY -
            mouse.y


          const distance =
            Math.sqrt(
              dx * dx +
              dy * dy
            )


          /* =========================
             INVISIBLE CURSOR FIELD
          ========================= */

          if (
            distance <
            INTERACTION_RADIUS
          ) {

            const normalizedDistance =
              1 -
              distance /
              INTERACTION_RADIUS


            const safeDistance =
              Math.max(
                distance,
                0.001
              )


            const force =
              normalizedDistance *
              normalizedDistance *
              REPULSION_STRENGTH *
              star.depth


            const pushX =
              dx /
              safeDistance *
              force

            const pushY =
              dy /
              safeDistance *
              force


            star.velocityX +=
              (
                pushX -
                star.velocityX
              ) * 0.08


            star.velocityY +=
              (
                pushY -
                star.velocityY
              ) * 0.08

          }


          /* =========================
             APPLY VELOCITY
          ========================= */

          star.x +=
            star.velocityX /
            width

          star.y +=
            star.velocityY /
            height


          /* =========================
             NATURAL DAMPING
          ========================= */

          star.velocityX *=
            0.88

          star.velocityY *=
            0.88


          /* =========================
             RETURN TO ORIGINAL
             POSITION
          ========================= */

          star.x +=
            (
              star.baseX -
              star.x
            ) *
            RETURN_SPEED

          star.y +=
            (
              star.baseY -
              star.y
            ) *
            RETURN_SPEED


          /* =========================
             KEEP STARS INSIDE FIELD
          ========================= */

          if (star.x < -0.05)
            star.x = 1.05

          if (star.x > 1.05)
            star.x = -0.05

          if (star.y < -0.05)
            star.y = 1.05

          if (star.y > 1.05)
            star.y = -0.05


          /* =========================
             CONVERT TO WEBGL SPACE
          ========================= */

          positions[index * 2] =
            star.x * 2 - 1

          positions[index * 2 + 1] =
            -(star.y * 2 - 1)

        }
      )


      /* =========================
         UPDATE POSITION BUFFER
      ========================= */

      gl.bindBuffer(
        gl.ARRAY_BUFFER,
        positionBuffer
      )

      gl.bufferData(
        gl.ARRAY_BUFFER,
        positions,
        gl.DYNAMIC_DRAW
      )


      gl.enableVertexAttribArray(
        positionLocation
      )

      gl.vertexAttribPointer(
        positionLocation,
        2,
        gl.FLOAT,
        false,
        0,
        0
      )


      /* =========================
         DRAW
      ========================= */

      gl.clearColor(
        0,
        0,
        0,
        0
      )

      gl.clear(
        gl.COLOR_BUFFER_BIT
      )


      gl.enable(
        gl.BLEND
      )

      gl.blendFunc(
        gl.SRC_ALPHA,
        gl.ONE
      )


      gl.drawArrays(
        gl.POINTS,
        0,
        STAR_COUNT
      )


      animationFrame =
        requestAnimationFrame(
          animate
        )

    }


    animationFrame =
      requestAnimationFrame(
        animate
      )


    /* =========================
       CLEANUP
    ========================= */

    return () => {

      cancelAnimationFrame(
        animationFrame
      )

      window.removeEventListener(
        "mousemove",
        handleMouseMove
      )

      window.removeEventListener(
        "mouseleave",
        handleMouseLeave
      )

      window.removeEventListener(
        "resize",
        resizeCanvas
      )

      gl.deleteBuffer(
        positionBuffer
      )

      gl.deleteBuffer(
        sizeBuffer
      )

      gl.deleteBuffer(
        brightnessBuffer
      )

      gl.deleteProgram(
        program
      )

      gl.deleteShader(
        vertexShader
      )

      gl.deleteShader(
        fragmentShader
      )

    }

  }, [])


  /* =========================
     SATELLITE ORBIT
  ========================= */

  useEffect(() => {

    const orbit =
      document.querySelector(".orbit-1")

    const satelliteElement =
      document.querySelector(".orbit-satellite")

    if (
      !orbit ||
      !satelliteElement
    ) return


    let animationFrame

    let lastTime =
      performance.now()


    let angle =
      Math.PI * 0.15


    /* Slow constant orbital speed */

    const orbitalSpeed =
      0.00028


    /* Satellite's own rotation */

    let satelliteRotation = 0

    const selfRotationSpeed =
      0.00008


    const animateSatellite =
      (time) => {

        const delta =
          Math.min(
            time - lastTime,
            32
          )

        lastTime =
          time


        /* =========================
           ORBIT
        ========================= */

        angle +=
          orbitalSpeed *
          delta


        const radiusX =
          orbit.clientWidth / 2

        const radiusY =
          orbit.clientHeight / 2


        const x =
          Math.cos(angle) *
          radiusX

        const y =
          Math.sin(angle) *
          radiusY


        /* =========================
           SELF ROTATION
        ========================= */

        satelliteRotation +=
          selfRotationSpeed *
          delta


        const rotationDegrees =
          satelliteRotation *
          57.2958


        /* =========================
           APPLY TRANSFORM
        ========================= */

        satelliteElement.style.transform = `
          translate(-50%, -50%)
          translate(${x}px, ${y}px)
          rotate(${rotationDegrees}deg)
        `


        animationFrame =
          requestAnimationFrame(
            animateSatellite
          )

      }


    animationFrame =
      requestAnimationFrame(
        animateSatellite
      )


    return () => {

      cancelAnimationFrame(
        animationFrame
      )

    }

  }, [])

  const scrollToAnalytics = () => {
    const el = document.getElementById("analytics");
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (

    <div className="app">


      {/* =========================
          WEBGL GALAXY STARFIELD
      ========================= */}

      <div
        className="starfield"
        style={{
          position: "fixed",
          inset: 0,
          width: "100%",
          height: "100%",
          pointerEvents: "none",
          zIndex: 0,
          overflow: "hidden"
        }}
      >

        <canvas
          ref={starCanvasRef}
          className="webgl-starfield"
          style={{
            display: "block",
            width: "100%",
            height: "100%"
          }}
        />

      </div>


      {/* =========================
          NAVBAR
      ========================= */}

      <nav className="navbar">

        <div className="brand">

          <img
            src={logo}
            alt="GeoNexus logo"
          />

          <div>

            <div className="brand-name">
              GeoNexus
            </div>

            <div className="brand-subtitle">
              EARTH INTELLIGENCE
            </div>

          </div>

        </div>


        <div className="nav-links">

          <a href="#vision">

            <span></span>

            VISION

          </a>


          <a href="#search">

            <span></span>

            SEARCH

          </a>


          <a href="#analytics">

            <span></span>

            ANALYTICS

          </a>


          <a href="#about">

            <span></span>

            ABOUT

          </a>

        </div>


        <div className="nav-right">

          <div className="status">

            <span className="status-dot"></span>

            SYSTEM ONLINE

          </div>


          <button className="explore-btn" onClick={scrollToAnalytics}>

            EXPLORE

            <span>→</span>

          </button>

        </div>

      </nav>


      {/* =========================
          HERO SECTION
      ========================= */}

      <section
        className="hero"
        id="vision"
      >


        {/* =========================
            LEFT CONTENT
        ========================= */}

        <div className="hero-content">

          <div className="platform-label">

            ───────── GEONEXUS PLATFORM V1.0

          </div>


          <h1>

            Turning Earth’s

            <br />

            Changes into

            <br />

            <span>
              Intelligence.
            </span>

          </h1>


          <p className="hero-description">

            Semantic retrieval and multi-temporal
            analysis of satellite imagery to detect,
            understand and monitor changes that matter.

          </p>


          <div className="hero-buttons">

            <button className="primary-btn" onClick={scrollToAnalytics}>

              EXPLORE DASHBOARD →

            </button>


            <button className="secondary-btn">

              LEARN MORE

            </button>

          </div>

        </div>


        {/* =========================
            EARTH VISUAL
        ========================= */}

        <div className="hero-visual">


          {/* LIVE DATA HUD */}

          <div className="hud-label">

            <span className="hud-dot"></span>

            LIVE SATELLITE DATA

          </div>


          {/* COORDINATES */}

          <div className="hud-coordinate">

            28.6139° N

            <br />

            77.2090° E

          </div>


          {/* =========================
              FIXED ORBIT 1
              SATELLITE ORBIT
          ========================= */}

          <div className="earth-orbit orbit-1">

            <img
              src={satellite}
              alt="GeoNexus satellite"
              className="orbit-satellite"
            />

          </div>


          {/* =========================
              ROTATING VISUAL ORBITS
          ========================= */}

          <div className="earth-orbit orbit-2"></div>

          <div className="earth-orbit orbit-3"></div>


          {/* =========================
              EARTH
          ========================= */}

          <img
            src={earth}
            alt="Earth satellite visualization"
            className="hero-earth"
          />

        </div>

      </section>
      <EarthChangesSection />

      <section
        id="analytics"
        style={{
          padding: "80px 40px",
          background: "#060b17",
          position: "relative",
          zIndex: 1
        }}
      >
        <h2 style={{
          color: "#38bdf8",
          textAlign: "center",
          fontSize: "1.5rem",
          letterSpacing: "0.15em",
          marginBottom: "12px",
          fontWeight: 700
        }}>
          SATELLITE CHANGE ANALYSIS
        </h2>
        <p style={{
          color: "#94a3b8",
          textAlign: "center",
          marginBottom: "36px",
          fontSize: "0.95rem"
        }}>
          Multi-temporal change detection across Indian cities
        </p>
        <Map />
      </section>

  <Process />
  <Section04/>
  <Section05 />
<Section06 />
    </div>

  )

}

export default App