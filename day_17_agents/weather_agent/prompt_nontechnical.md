# Weather Prediction Agent — Plain English Guide

---

## What Is This?

This is a smart assistant that **predicts tomorrow's maximum temperature**
for any city in the world.

You tell it a city name. It looks up the actual temperatures from the past
7 days, figures out whether it has been getting hotter or cooler, and then
makes an educated prediction about tomorrow — just like a weather analyst
would do by hand, but in seconds.

At the end, it also shows you the official weather forecast so you can
compare and see how close it got.

---

## Who Is It For?

Anyone who wants a quick, honest temperature prediction without opening
a weather app — farmers, travellers, event planners, teachers, students,
or just curious people.

---

## How to Use It

1. Open your terminal (the black window where you type commands).
2. Run the program and type your city name when asked.
3. Watch it think out loud — it will show you each step it takes.
4. Read the final prediction and compare it with the official forecast.

**Example — what you type:**
```
City: Hyderabad
```

**Example — what you see:**
```
Thinking... looking up past temperatures for Hyderabad
Thinking... calculating the temperature trend
Prediction: Tomorrow's maximum will be around 31°C.
The past week shows a slight downward trend of -0.3°C per day,
suggesting a mild cool-down from the recent high of 32°C.

Official forecast for tomorrow → max 31.2°C, min 20.8°C
```

---

## What Questions Can You Ask?

Just give it a city name. That's it. Examples:

- `Mumbai`
- `London`
- `New York`
- `Tokyo`
- `Nairobi`

---

## What It Does Behind the Scenes
*(You don't need to know this to use it — just for the curious)*

1. It checks a free weather website for the past 7 days of temperatures.
2. It calculates whether temperatures have been rising or falling.
3. It uses an AI brain (running on your computer) to make the prediction.
4. It compares its guess with the website's official forecast.

No internet subscription, no paid service, no personal data needed.

---

## What It Cannot Do

- It cannot predict rain, wind, or humidity — only temperature.
- It cannot predict more than one day ahead.
- It may be less accurate for cities with unusual or rapidly changing weather.
- It needs your computer to have the AI model already installed.

---

## Limitations to Know

| Situation | What Happens |
|---|---|
| You type a city that doesn't exist | It tells you the city wasn't found |
| The weather has been very unpredictable | The prediction may be less accurate |
| No internet connection | It cannot fetch weather data |

---

## In Simple Words

> "Tell me a city. I'll look at its recent weather, spot the pattern,
> and give you my best guess for tomorrow — then show you the real forecast
> so you can judge for yourself."
