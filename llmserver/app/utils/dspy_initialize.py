import dspy


def check_dspy(app):
    print("Middleware: Checking dspy configuration")

    if not dspy.settings.lm or not dspy.settings.rm:
        print(
            "\033[91m Setting up dspy \033[0m",
            "lm: ",
            dspy.settings.lm,
            " / rm: ",
            dspy.settings.rm,
        )
        turbo = dspy.OpenAI(model="gpt-3.5-turbo")
        colbertv2_wiki17_abstracts = dspy.ColBERTv2(
            url="http://20.102.90.50:2017/wiki17_abstracts"
        )
        dspy.settings.configure(lm=turbo, rm=colbertv2_wiki17_abstracts)
        print(
            "\033[91m After setting up dspy \033[0m",
            "lm: ",
            dspy.settings.lm,
            " / rm: ",
            dspy.settings.rm,
        )
    else:
        print("\033[92m dspy configuration already set \033[0m")

    return app
