from src.models.mini_venmo import MiniVenmo

if __name__ == '__main__':
    venmo = MiniVenmo()

    bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
    carol = venmo.create_user("Carol", 10.00, "4242424242424242")

    try:
        bobby.pay(carol, 5.00, "Coffee")
        carol.pay(bobby, 15.00, "Lunch")
    except Exception as e:
        print(e)

    bobby.add_friend(carol)

    feed = bobby.retrieve_feed()
    venmo.render_feed(feed)
