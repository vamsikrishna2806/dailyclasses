def is_prime(number):
	if number < 2:
		return False

	divisor = 2
	while divisor * divisor <= number:
		if number % divisor == 0:
			return False
		divisor += 1

	return True


number = int(input("Enter an integer: "))

if is_prime(number):
	print(f"{number} is a prime number.")
	print(f"{number} is not a prime number.")
